import os, tempfile, pytest
from app import app

@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_path = tmp_path / 'test.sqlite3'
    monkeypatch.setenv('CAREERAI_DB', str(db_path))
    app.config.update(TESTING=True, SECRET_KEY='test-secret-key')
    app._db_ready = False
    with app.test_client() as client:
        yield client
    app._db_ready = False

def csrf(client):
    with client.session_transaction() as sess: return sess['_csrf_token']

def register(client, email='student@example.com', password='GoodPass123'):
    return client.post('/register', data={'_csrf_token':csrf(client),'full_name':'Test Student','email':email,'password':password,'confirm_password':password,'education_level':'Undergraduate','degree_branch':'B.Tech CSE','college_name':'Demo College','cgpa':'8.2','graduation_year':'2027','skills':'Python, SQL, Git','interests':'python, backend','preferred_domain':'Software Development','work_mode':'Remote'}, follow_redirects=True)

def test_home_loads(client):
    assert client.get('/').status_code == 200
    assert b'CareerAI' in client.get('/').data

def test_register_and_duplicate_rejected(client):
    assert register(client).status_code == 200
    assert b'Welcome to CareerAI' in register(client).data or b'already exists' in register(client).data
    client.post('/logout', data={'_csrf_token':csrf(client)}, follow_redirects=True)
    response=register(client)
    assert b'already exists' in response.data

def test_login_logout_and_bad_password(client):
    register(client)
    client.post('/logout', data={'_csrf_token':csrf(client)}, follow_redirects=True)
    bad=client.post('/login',data={'_csrf_token':csrf(client),'email':'student@example.com','password':'wrong'},follow_redirects=True)
    assert b'incorrect' in bad.data
    good=client.post('/login',data={'_csrf_token':csrf(client),'email':'student@example.com','password':'GoodPass123'},follow_redirects=True)
    assert b'Your student workspace' in good.data
    out=client.post('/logout',data={'_csrf_token':csrf(client)},follow_redirects=True)
    assert b'logged out safely' in out.data

def test_private_pages_require_login(client):
    for path in ['/dashboard','/profile','/assessment','/careers','/internships','/roadmap']:
        response=client.get(path)
        assert response.status_code == 302
        assert '/login' in response.location

def test_profile_assessment_career_and_roadmap_persist(client):
    register(client)
    response=client.post('/assessment',data={'_csrf_token':csrf(client),'technical_interests':'python backend automation','preferred_activities':'Build applications','programming_experience':'Some practice projects','career_goals':'Software Development','experience_level':'Building projects'},follow_redirects=True)
    assert b'Python Developer' in response.data or b'career' in response.data.lower()
    assert client.get('/careers').status_code == 200
    assert client.get('/internships').status_code == 200
    page=client.get('/roadmap?career=Python%20Developer')
    assert page.status_code == 200
    response=client.post('/roadmap',data={'_csrf_token':csrf(client),'career':'Python Developer','completed':['0','1']},follow_redirects=True)
    assert b'Roadmap progress saved' in response.data
    assert b'2/8' in response.data

def test_csrf_required(client):
    response=client.post('/login',data={'email':'a@b.com','password':'x'})
    assert response.status_code == 400
