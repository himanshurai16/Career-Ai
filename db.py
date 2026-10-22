import os, sqlite3
DEFAULT_DB_PATH=os.path.join(os.path.dirname(__file__),'careerai.sqlite3')

def get_db():
    db_path=os.environ.get('CAREERAI_DB') or DEFAULT_DB_PATH
    conn=sqlite3.connect(db_path); conn.row_factory=sqlite3.Row; conn.execute('PRAGMA foreign_keys=ON'); return conn

def init_db():
    with get_db() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT NOT NULL UNIQUE COLLATE NOCASE,password_hash TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS profiles(user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,education_level TEXT NOT NULL DEFAULT 'Undergraduate',degree_branch TEXT NOT NULL DEFAULT '',college_name TEXT NOT NULL DEFAULT '',cgpa TEXT NOT NULL DEFAULT '',graduation_year TEXT NOT NULL DEFAULT '',skills TEXT NOT NULL DEFAULT '',interests TEXT NOT NULL DEFAULT '',preferred_domain TEXT NOT NULL DEFAULT 'Software Development',work_mode TEXT NOT NULL DEFAULT 'Any');
        CREATE TABLE IF NOT EXISTS assessments(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,technical_interests TEXT NOT NULL,preferred_activities TEXT NOT NULL,programming_experience TEXT NOT NULL,career_goals TEXT NOT NULL,experience_level TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS internships(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,company TEXT NOT NULL,required_skills TEXT NOT NULL,domain TEXT NOT NULL,work_mode TEXT NOT NULL,location TEXT NOT NULL,eligibility TEXT NOT NULL,application_url TEXT,source TEXT NOT NULL DEFAULT 'Fictional CareerAI demo record',is_demo INTEGER NOT NULL DEFAULT 1);
        CREATE TABLE IF NOT EXISTS roadmap_progress(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,career TEXT NOT NULL,step_key TEXT NOT NULL,completed INTEGER NOT NULL DEFAULT 0 CHECK(completed IN (0,1)),updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,career,step_key));
        ''')

def seed_db():
    demo=[
    ('Python Development Intern','DemoTech Learning Lab','Python, SQL, Git, Flask','Software Development','Remote','Demo location','Students familiar with Python basics',None),
    ('Frontend Web Intern','PixelPath Demo Studio','HTML, CSS, JavaScript, Git','Web Development','Hybrid','Lucknow (fictional demo)','Basic HTML/CSS/JavaScript knowledge',None),
    ('Data Analytics Intern','InsightBridge Demo Lab','Python, pandas, SQL, Excel','Data Analytics','Remote','Demo location','Basic statistics and spreadsheet skills',None),
    ('AI/ML Learning Intern','ModelGarden Demo Studio','Python, NumPy, pandas, scikit-learn','AI & Machine Learning','On-site','Gorakhpur (fictional demo)','Python basics and interest in machine learning',None),
    ('Cybersecurity Trainee','SafeNet Demo Academy','Networking, Linux, Python','Cybersecurity','Hybrid','Demo location','Networking fundamentals',None),
    ('Cloud Support Intern','CloudSteps Demo Lab','Linux, Git, Networking, AWS basics','Cloud Computing','Remote','Demo location','Basic operating system and networking concepts',None),
    ('Software Engineering Intern','BuildBetter Demo Studio','Python, Java, SQL, Git, DSA','Software Development','On-site','Demo location','Currently enrolled student',None),
    ('UI Web Design Intern','BrightCanvas Demo Studio','HTML, CSS, JavaScript, UI/UX','Web Development','Remote','Demo location','Portfolio or class projects helpful',None)]
    with get_db() as db:
        count=db.execute('SELECT COUNT(*) n FROM internships').fetchone()['n']
        if not count: db.executemany('INSERT INTO internships(title,company,required_skills,domain,work_mode,location,eligibility,application_url,source,is_demo) VALUES(?,?,?,?,?,?,?,?,?,1)',[(a,b,c,d,e,f,g,h,'Fictional demo data; not an active vacancy') for a,b,c,d,e,f,g,h in demo])
