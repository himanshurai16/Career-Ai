import re, sqlite3

CAREERS=[
 {'title':'Python Developer','domain':'Software Development','description':'Build backend services, automation tools and data-driven applications with Python.','skills':['Python','SQL','Git','Flask','REST APIs','Testing'],'interests':['python','automation','backend','programming','software','api'],'activities':['build applications','solve coding problems','automate tasks'],'projects':['Build a student task tracker with Flask and SQLite','Create a CSV data-cleaning command-line tool'],'roadmap':['Python fundamentals','Functions, OOP and data structures','SQL and database concepts','Git and GitHub','Flask web applications','REST API development','Build and document portfolio projects','Practice coding interviews']},
 {'title':'Web Developer','domain':'Web Development','description':'Create accessible, responsive websites and interactive web applications.','skills':['HTML','CSS','JavaScript','Git','Responsive Design','Flask'],'interests':['web','frontend','website','design','javascript','ui'],'activities':['design interfaces','build websites','create interactive pages'],'projects':['Create a responsive personal portfolio','Build a searchable campus events website'],'roadmap':['HTML semantics and accessibility','CSS layout, flexbox and grid','JavaScript fundamentals','Responsive UI and forms','Git and GitHub','Connect a Flask backend','Deploy a portfolio project','Web interview practice']},
 {'title':'Software Developer','domain':'Software Development','description':'Design, implement, test and maintain reliable software systems.','skills':['Python','Java','Data Structures','Algorithms','SQL','Git','Testing'],'interests':['software','programming','problem solving','algorithms','applications'],'activities':['solve coding problems','design software','debug programs'],'projects':['Build a library management application','Implement a data-structures visualizer'],'roadmap':['Programming fundamentals','Data structures and algorithms','Object-oriented design','SQL and databases','Git and collaborative workflow','Testing and debugging','Build a complete software project','Prepare for technical interviews']},
 {'title':'Data Analyst','domain':'Data Analytics','description':'Turn structured data into clear insights using analysis, visualization and statistics.','skills':['Python','SQL','pandas','NumPy','Excel','Data Visualization','Statistics'],'interests':['data','analytics','statistics','business','visualization','research'],'activities':['analyze datasets','find patterns','create charts and reports'],'projects':['Analyze public transport or weather CSV data','Create a dashboard with charts and key metrics'],'roadmap':['Spreadsheet and data-cleaning basics','SQL queries and joins','Python fundamentals','pandas and NumPy','Descriptive statistics','Data visualization','Build an analysis portfolio','Practice case studies']},
 {'title':'AI/ML Engineer','domain':'AI & Machine Learning','description':'Develop data-informed models and integrate machine learning into useful products.','skills':['Python','NumPy','pandas','scikit-learn','Statistics','SQL','Model Evaluation'],'interests':['ai','machine learning','ml','data','prediction','intelligent systems'],'activities':['experiment with datasets','build predictive models','evaluate model results'],'projects':['Train a transparent student-support classifier on a toy dataset','Build a movie or course recommender with documented limits'],'roadmap':['Python programming','NumPy and pandas','Probability and statistics','Supervised learning concepts','scikit-learn pipelines','Model evaluation and data leakage','Build and explain an ML project','ML interview fundamentals']},
 {'title':'Cybersecurity Analyst','domain':'Cybersecurity','description':'Help protect systems by understanding networks, security controls and risk.','skills':['Networking','Linux','Python','Security Fundamentals','Log Analysis','SQL'],'interests':['security','cyber','privacy','network','linux','investigation'],'activities':['investigate system logs','learn networking','identify risks'],'projects':['Analyze sample authentication logs','Create a personal security checklist for a demo app'],'roadmap':['Computer and network fundamentals','Linux command line','Security and privacy basics','Python scripting','Log analysis and monitoring','Web security fundamentals','Document a defensive lab project','Ethics and interview preparation']},
 {'title':'Cloud Engineer','domain':'Cloud Computing','description':'Deploy and operate applications using cloud concepts, automation and reliable infrastructure.','skills':['Linux','Networking','Git','Python','Cloud Fundamentals','Docker','CI/CD'],'interests':['cloud','infrastructure','devops','servers','deployment','network'],'activities':['configure environments','automate deployment','troubleshoot systems'],'projects':['Containerize a Flask app locally','Write a deployment checklist and CI workflow'],'roadmap':['Linux and command line','Networking fundamentals','Git and scripting','Cloud computing concepts','Containers with Docker','CI/CD fundamentals','Deploy a demo application','Cloud fundamentals revision']}
]

def tokens(s): return {re.sub(r'[^a-z0-9+#.]','',x.lower().strip()) for x in re.split(r'[,;\n|]',s or '') if x.strip()}
def match_skills(student, required):
    have=tokens(student); req=[s.strip() for s in re.split(r'[,;]',required or '') if s.strip()]
    matched=[]; missing=[]
    for s in req:
        norm=re.sub(r'[^a-z0-9+#.]','',s.lower())
        (matched if any(norm==h or norm in h or h in norm for h in have if norm and h) else missing).append(s)
    return matched,missing

def recommend_careers(profile):
    skills=profile.get('skills',''); interests=' '.join([profile.get('interests',''),profile.get('preferred_domain',''),profile.get('degree_branch','')]).lower()
    results=[]
    for c in CAREERS:
        matched,missing=match_skills(skills, ','.join(c['skills']))
        interest_hits=sum(1 for term in c['interests'] if term in interests)
        domain_hit=profile.get('preferred_domain','').lower() in (c['domain'].lower(),c['title'].lower())
        score=min(98,round(25+min(40,interest_hits*9)+min(30,len(matched)*7)+(8 if domain_hit else 0)))
        why=[]
        if domain_hit: why.append('It aligns with your preferred career domain.')
        if interest_hits: why.append(f'{interest_hits} interest/domain signals align with this path.')
        if matched: why.append('Your listed skills include '+', '.join(matched[:4])+'.')
        if not why: why.append('This is a useful exploratory path; complete the assessment to personalize your matches further.')
        results.append({**c,'score':score,'matched':matched,'missing':missing,'why':why})
    return sorted(results,key=lambda x:(x['score'],len(x['matched'])),reverse=True)

def match_internships(profile,query='',domain='',mode='',skill='',limit=100):
    from db import get_db
    have=profile.get('skills','')
    with get_db() as db: rows=[dict(r) for r in db.execute('SELECT * FROM internships ORDER BY title')]
    out=[]
    for r in rows:
        hay=' '.join([r['title'],r['company'],r['domain'],r['required_skills'],r['location']]).lower()
        if query and query.lower() not in hay: continue
        if domain and r['domain']!=domain: continue
        if mode and r['work_mode'].lower()!=mode.lower(): continue
        if skill and skill.lower() not in r['required_skills'].lower(): continue
        matched,missing=match_skills(have,r['required_skills'])
        required=[x for x in re.split(r'[,;]',r['required_skills']) if x.strip()]
        score=round(100*len(matched)/len(required)) if required else 0
        if profile.get('preferred_domain','').lower() in r['domain'].lower(): score=min(100,score+10)
        if profile.get('work_mode') in ('Remote','Hybrid','On-site') and profile['work_mode']==r['work_mode']: score=min(100,score+5)
        out.append({**r,'matched':matched,'missing':missing,'score':score,'is_demo':bool(r['is_demo'])})
    return sorted(out,key=lambda x:(x['score'],x['title']),reverse=True)[:limit]

def make_roadmap(career):
    c=next((c for c in CAREERS if c['title']==career),CAREERS[0])
    return [{'title':step,'resource':'https://www.google.com/search?q='+step.replace(' ','+'), 'project': c['projects'][i%len(c['projects'])] if i in (2,5,6) else ''} for i,step in enumerate(c['roadmap'])]

def profile_completion(p):
    fields=['full_name','email','education_level','degree_branch','college_name','cgpa','graduation_year','skills','interests','preferred_domain','work_mode']
    return round(100*sum(1 for f in fields if str(p.get(f,'')).strip())/len(fields))
