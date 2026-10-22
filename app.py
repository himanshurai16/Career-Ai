import os, re, secrets, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import init_db, get_db, seed_db
from recommender import recommend_careers, match_internships, make_roadmap, profile_completion

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32), SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
if os.environ.get('COOKIE_SECURE') == '1': app.config['SESSION_COOKIE_SECURE'] = True

@app.before_request
def setup():
    if not getattr(app, '_db_ready', False):
        init_db(); seed_db(); app._db_ready = True
    if request.method == 'POST':
        token = session.get('_csrf_token')
        supplied = request.form.get('_csrf_token', '')
        if not token or not secrets.compare_digest(token, supplied): abort(400, 'Invalid form security token. Refresh and try again.')

@app.context_processor
def inject_globals():
    if '_csrf_token' not in session: session['_csrf_token'] = secrets.token_urlsafe(24)
    return {'csrf_token': session['_csrf_token'], 'current_user': session.get('user_name'), 'current_endpoint': request.endpoint}

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access your student workspace.', 'info'); return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper

def get_profile(user_id=None):
    uid = user_id or session.get('user_id')
    with get_db() as db:
        row = db.execute('SELECT u.full_name,u.email,p.* FROM users u JOIN profiles p ON p.user_id=u.id WHERE u.id=?', (uid,)).fetchone()
    return dict(row) if row else {}

def user_skills(profile):
    return [s.strip() for s in (profile.get('skills') or '').split(',') if s.strip()]

@app.route('/')
def home(): return render_template('home.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if session.get('user_id'): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        f = request.form
        name, email, password = f.get('full_name','').strip(), f.get('email','').strip().lower(), f.get('password','')
        if len(name) < 2 or len(name) > 100: flash('Enter a name between 2 and 100 characters.', 'error')
        elif not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email): flash('Enter a valid email address.', 'error')
        elif len(password) < 8: flash('Password must contain at least 8 characters.', 'error')
        elif password != f.get('confirm_password'): flash('Passwords do not match.', 'error')
        else:
            try:
                with get_db() as db:
                    cur = db.execute('INSERT INTO users(full_name,email,password_hash) VALUES(?,?,?)', (name,email,generate_password_hash(password)))
                    uid = cur.lastrowid
                    db.execute('INSERT INTO profiles(user_id,education_level,degree_branch,college_name,cgpa,graduation_year,skills,interests,preferred_domain,work_mode) VALUES(?,?,?,?,?,?,?,?,?,?)', (uid,f.get('education_level','Undergraduate'),f.get('degree_branch','').strip(),f.get('college_name','').strip(),f.get('cgpa','').strip(),f.get('graduation_year','').strip(),f.get('skills','').strip(),f.get('interests','').strip(),f.get('preferred_domain','Software Development'),f.get('work_mode','Any')))
                session.clear(); session['user_id']=uid; session['user_name']=name; session['_csrf_token']=secrets.token_urlsafe(24)
                flash('Welcome to CareerAI! Your account is ready.', 'success'); return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError: flash('An account with this email already exists.', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if session.get('user_id'): return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email=request.form.get('email','').strip().lower(); password=request.form.get('password','')
        with get_db() as db: user=db.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.clear(); session['user_id']=user['id']; session['user_name']=user['full_name']; session['_csrf_token']=secrets.token_urlsafe(24)
            flash('You are now logged in.', 'success'); return redirect(request.args.get('next') if (request.args.get('next') or '').startswith('/') and not (request.args.get('next') or '').startswith('//') else url_for('dashboard'))
        flash('Email or password is incorrect.', 'error')
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout(): session.clear(); flash('You have logged out safely.', 'success'); return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    p=get_profile(); careers=recommend_careers(p); internships=match_internships(p, limit=3)
    with get_db() as db:
        total=db.execute('SELECT COUNT(*) n FROM roadmap_progress WHERE user_id=?',(session['user_id'],)).fetchone()['n']
        done=db.execute('SELECT COUNT(*) n FROM roadmap_progress WHERE user_id=? AND completed=1',(session['user_id'],)).fetchone()['n']
        assessed=db.execute('SELECT COUNT(*) n FROM assessments WHERE user_id=?',(session['user_id'],)).fetchone()['n']
    return render_template('dashboard.html',profile=p,completion=profile_completion(p),careers=careers[:3],internships=internships,roadmap_done=done,roadmap_total=total,assessed=assessed)

@app.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        f=request.form; year=f.get('graduation_year','').strip(); cgpa=f.get('cgpa','').strip()
        if year and (not year.isdigit() or not 2000 <= int(year) <= 2100): flash('Graduation year must be between 2000 and 2100.', 'error')
        elif cgpa and (not re.fullmatch(r'\d{1,2}(\.\d{1,2})?',cgpa) or float(cgpa)>100): flash('Enter a valid CGPA or percentage (0–100).', 'error')
        else:
            with get_db() as db:
                db.execute('UPDATE users SET full_name=? WHERE id=?',(f.get('full_name','').strip()[:100],session['user_id']))
                db.execute('UPDATE profiles SET education_level=?,degree_branch=?,college_name=?,cgpa=?,graduation_year=?,skills=?,interests=?,preferred_domain=?,work_mode=? WHERE user_id=?',(f.get('education_level',''),f.get('degree_branch','').strip(),f.get('college_name','').strip(),cgpa,year,f.get('skills','').strip(),f.get('interests','').strip(),f.get('preferred_domain','Software Development'),f.get('work_mode','Any'),session['user_id']))
                db.commit(); session['user_name']=f.get('full_name','Student').strip() or 'Student'
            flash('Profile updated successfully.', 'success'); return redirect(url_for('profile'))
    return render_template('profile.html',profile=get_profile())

@app.route('/assessment', methods=['GET','POST'])
@login_required
def assessment():
    p=get_profile()
    if request.method=='POST':
        answers={k:request.form.get(k,'').strip() for k in ['technical_interests','preferred_activities','programming_experience','career_goals','experience_level']}
        with get_db() as db:
            db.execute('INSERT INTO assessments(user_id,technical_interests,preferred_activities,programming_experience,career_goals,experience_level) VALUES(?,?,?,?,?,?)',(session['user_id'],answers['technical_interests'],answers['preferred_activities'],answers['programming_experience'],answers['career_goals'],answers['experience_level']))
            db.execute('UPDATE profiles SET interests=?,preferred_domain=? WHERE user_id=?',(answers['technical_interests'],answers['career_goals'] or p.get('preferred_domain') or 'Software Development',session['user_id']))
            db.commit()
        flash('Assessment saved. Your career matches have been refreshed.', 'success'); return redirect(url_for('careers'))
    with get_db() as db: last=db.execute('SELECT * FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 1',(session['user_id'],)).fetchone()
    return render_template('assessment.html',profile=p,assessment=dict(last) if last else {})

@app.route('/careers')
@login_required
def careers():
    p=get_profile()
    with get_db() as db: a=db.execute('SELECT * FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 1',(session['user_id'],)).fetchone()
    if a:
        p['interests']=', '.join(filter(None,[p.get('interests',''),a['technical_interests'],a['preferred_activities'],a['career_goals']]))
        if a['career_goals']: p['preferred_domain']=a['career_goals']
    return render_template('careers.html',careers=recommend_careers(p),profile=p)

@app.route('/internships')
@login_required
def internships():
    p=get_profile(); q=request.args.get('q','').strip()[:100]; domain=request.args.get('domain',''); mode=request.args.get('mode',''); skill=request.args.get('skill','').strip()[:60]
    rows=match_internships(p,query=q,domain=domain,mode=mode,skill=skill,limit=100)
    with get_db() as db: domains=[r['domain'] for r in db.execute('SELECT DISTINCT domain FROM internships ORDER BY domain')]
    return render_template('internships.html',internships=rows,domains=domains,filters={'q':q,'domain':domain,'mode':mode,'skill':skill})

@app.route('/roadmap', methods=['GET','POST'])
@login_required
def roadmap():
    p=get_profile(); career=request.values.get('career','')
    available=recommend_careers(p)
    names={c['title'] for c in available}
    if career not in names: career=available[0]['title'] if available else 'Python Developer'
    steps=make_roadmap(career)
    if request.method=='POST':
        checked=set(request.form.getlist('completed'))
        with get_db() as db:
            for i,step in enumerate(steps):
                db.execute('INSERT INTO roadmap_progress(user_id,career,step_key,completed) VALUES(?,?,?,?) ON CONFLICT(user_id,career,step_key) DO UPDATE SET completed=excluded.completed',(session['user_id'],career,str(i),1 if str(i) in checked else 0))
            db.commit()
        flash('Roadmap progress saved.', 'success'); return redirect(url_for('roadmap',career=career))
    with get_db() as db: done={r['step_key'] for r in db.execute('SELECT step_key FROM roadmap_progress WHERE user_id=? AND career=? AND completed=1',(session['user_id'],career))}
    for i,s in enumerate(steps): s['key']=str(i); s['completed']=str(i) in done
    return render_template('roadmap.html',steps=steps,careers=available,selected=career,done=len(done),total=len(steps))

@app.errorhandler(400)
def bad_request(e): return render_template('error.html',code=400,message=getattr(e,'description','Bad request')),400
@app.errorhandler(404)
def not_found(e): return render_template('error.html',code=404,message='The page you requested could not be found.'),404

if __name__=='__main__': app.run(debug=os.environ.get('FLASK_DEBUG')=='1')
