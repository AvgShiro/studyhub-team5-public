# StudyHub - Team 5 (Platform & Data Privacy)

Login and roles, user profiles, GDPR export/deletion. Other teams depend on this.

## Setup (once)
    python -m venv .venv
    source .venv/bin/activate        # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

## Run
Real service (SQLite, hashed passwords, JWT tokens):
    uvicorn app.main:app --reload --port 8000

Mock API (fake data in memory, for other teams to build against today):
    uvicorn mock_api:app --reload --port 8000

Open http://localhost:8000/docs to try every endpoint in the browser.
Test accounts (both versions):
    student@th-deg.de / test123      admin@th-deg.de / admin123

## Test
    pytest

## Layout
    mock_api.py        fake API, same URLs/shapes as the real one
    app/               the real service
      main.py          app entry point, test-user seeding
      database.py      database connection
      models.py        database tables
      schemas.py       API request/response shapes (the contract)
      auth.py          passwords, tokens, role checks
      gdpr_hooks.py    where other teams register export/delete functions
      routes/          login.py, users.py, gdpr.py
    identity_lib/      functions other teams import (verify_token, get_user)
    tests/             pytest tests

## Before real use
- Set TEAM5_SECRET to a long random value (the default is for development).
- Agree the contract (user_id type, roles, endpoints) with the other teams.
