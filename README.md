<<<<<<< HEAD
# CareerAI — Student Career & Internship Advisor

CareerAI is a full-stack college mini project built with Python Flask, SQLite, HTML, CSS and JavaScript. It helps students explore possible career paths, compare skills with fictional internship examples, and track a learning roadmap.

## Features

- Student registration, secure password hashing, login/logout and session-protected routes.
- CSRF tokens on POST forms, parameterized SQL queries, server-side validation and secure cookie defaults.
- Student profile creation and editing.
- Career assessment saved in SQLite.
- Explainable career recommendation scoring for Python Developer, Web Developer, Software Developer, Data Analyst, AI/ML Engineer, Cybersecurity Analyst and Cloud Engineer.
- Skill-gap comparison, starter project ideas and career-specific learning steps.
- Internship search and filters for domain, work mode and skills, with skill-overlap match scores.
- SQLite persistence for roadmap completion.
- Responsive UI with shared navigation, flash feedback and mobile menu.
- Automated tests for the primary user journeys.

## Recommendation method

The project currently uses a transparent **rule-based scoring system**, not a trained ML model. Career scores combine preferred domain, keyword signals from the student's interests/branch, and listed skills. Internship matching compares normalized skill names against each demo record's required skills, then applies small preferred-domain and work-mode bonuses. Scores are heuristic guidance, not a prediction of employability. The project does not claim that a machine-learning model has been trained. scikit-learn, pandas and NumPy are not required for this deterministic version.

## Internship data notice

Every seeded internship record is explicitly fictional demo data. Company names, locations and opportunities are examples for demonstrating the application; they are **not active vacancies**. No application URLs are fabricated or provided. To use real opportunities, replace the seed data with verified records and their genuine source URLs.

## Requirements

- Python 3.10 or newer recommended
- pip
- A modern browser

## Run on Windows

Open Command Prompt or PowerShell in the `CareerAI` folder:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a secret key and set it in your terminal (recommended for your local run):

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

Start the application:

```powershell
python app.py
```

Open <http://127.0.0.1:5000>. SQLite tables and fictional demo internship records are created automatically on first application request. The database file `careerai.sqlite3` appears in the project directory. Keep this file private because it contains student profile records and password hashes.

To run in development with Flask debug enabled, set `$env:FLASK_DEBUG = "1"` before `python app.py`. Do not enable debug mode on a public server. For HTTPS deployment, set `COOKIE_SECURE=1` and use a strong environment-provided `SECRET_KEY`.

## Run tests

From the project root:

```powershell
pytest -q
```

The tests use a temporary SQLite database and do not overwrite your local student database.

## Folder structure

```text
CareerAI/
├── app.py
├── db.py
├── recommender.py
├── requirements.txt
├── README.md
├── .env.example
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── assessment.html
│   ├── careers.html
│   ├── internships.html
│   ├── roadmap.html
│   └── error.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── tests/test_app.py
```

## College demonstration script (about 3 minutes)

1. **Introduction (20 sec):** “CareerAI is a student career and internship advisor. It brings profile management, explainable career matching, skill gaps and a saved learning roadmap into one application.”
2. **Register (30 sec):** Create a demo student account using a made-up email and a password with at least 8 characters. Add skills such as Python, HTML, SQL and Git.
3. **Dashboard (20 sec):** Show profile completion, career matches, demo internship matches and roadmap progress.
4. **Assessment (30 sec):** Select interests and preferred activities, submit, and explain that responses are saved in SQLite.
5. **Career matches (30 sec):** Open Careers. Point out the match score, explanation, skills already listed and skills to learn. Explain that the scoring is rule-based and interpretable.
6. **Internships (25 sec):** Search for Python or filter by remote/domain. Point out matching and missing skills and the clear fictional-demo notice.
7. **Roadmap (25 sec):** Mark the first two learning steps completed, save, refresh and show the saved progress.
8. **Close (20 sec):** Show the profile editor and explain the stack: Flask, SQLite, secure password hashing, CSRF protection and responsive HTML/CSS/JS.

## Limitations and next steps

- Career and internship scores are simple heuristic scores; they should not be interpreted as scientifically validated predictions.
- The internship records are fictional demos, not live listings.
- The resource links perform a Google search for the step title rather than claiming a specific course is endorsed or available.
- Email verification, password reset, rate limiting, administrator data management and production deployment configuration are not implemented.
- Google Fonts is an optional visual enhancement; the app's core features do not need an API key or paid service. If offline use is required, remove the font import at the top of `static/css/style.css`.
=======
# Career-Ai
>>>>>>> 1551d2c507d3001f7ace9da7790743608ca4084b
