# StudyHub - Team 5: Platform & Data Privacy

Team 5 builds the foundation the other StudyHub teams rely on:

- **Login and roles** (`student`, `admin`)
- **User profiles**
- **GDPR** data export and deletion
- **A shared UI design system** (not in this repo yet)

This repository contains two versions of the same identity API:

| Version | File | Purpose |
|---------|------|---------|
| **Mock** | `mock_api.py` | A fake API with fixed users and fake tokens. Use it **today** to build your own team's features without waiting for us. |
| **Real** | `app/` | The actual service: database, hashed passwords, signed tokens. |

Both use the **same URLs and fields**, so you can switch from the mock to the real one without changing your code.

> **Status:** draft (v0.1). The URLs and fields are still being agreed with the other teams.

---

## Quick start: run the mock API

You need **Python 3.10 or newer**. Check with `python --version` (on macOS/Linux it may be `python3 --version`).

### 1. Get the code

```
git clone https://github.com/AvgShiro/studyhub-team5-public.git
cd studyhub-team5
```

### 2. Create a virtual environment and install packages

A virtual environment keeps this project's packages separate from the rest of your computer.

**Windows (PowerShell)**
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell says scripts are disabled, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

**Windows (Command Prompt)**
```
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

**macOS / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You'll see `(.venv)` at the start of your terminal line when it's active. Run the activate command again each time you open a new terminal.

### 3. Start the mock

```
uvicorn mock_api:app --port 8001
```
Port 8001 avoids clashing with your own service if it uses 8000. Add `--reload` if you're editing the file and want automatic restarts.

### 4. Try it

Open **http://localhost:8001/docs** in your browser. It lists every endpoint and lets you try them.

1. Open `POST /auth/login`, click **Try it out**, and send:
   ```json
   {"email": "student@th-deg.de", "password": "test123"}
   ```
2. You get back `{"token": "...", "user_id": 1, "role": "student"}`.
3. Call a protected endpoint by sending that token in a header:
   ```
   curl http://localhost:8001/users/me -H "Authorization: Bearer <your token>"
   ```
   (The `/docs` page does not send the token for you yet, so use curl or your own code for protected endpoints. On Windows Command Prompt, use `curl.exe`.)

**Test accounts**

| Email | Password | Role |
|-------|----------|------|
| student@th-deg.de | test123 | student |
| admin@th-deg.de | admin123 | admin |

**To stop the server:** click the terminal and press `Ctrl + C`.

### What the mock offers

| Method and URL | What it does |
|----------------|--------------|
| `POST /auth/login` | Log in, returns token, `user_id`, `role` |
| `GET /users/me` | Your own user |
| `PATCH /users/me` | Change your name |
| `GET /users/{user_id}` | Look up another user |
| `GET /admin/ping` | Example admin-only endpoint (403 for students) |
| `GET /users/me/export` | GDPR export (placeholder data in the mock) |
| `DELETE /users/me` | GDPR deletion (removes the mock user) |

---

## Launching the mock and the real API

Run these from the project's root folder (where `mock_api.py` is), with your virtual environment active (see step 2 above).

| | Mock API | Real API |
|---|---|---|
| **Command** | `uvicorn mock_api:app --port 8001` | `uvicorn app.main:app --port 8000` |
| **Docs page** | http://localhost:8001/docs | http://localhost:8000/docs |
| **Data** | Fake, in memory, resets on restart | Stored in `team5.db`, kept between restarts |

Add `--reload` to either command to restart automatically when you edit code (for example `uvicorn app.main:app --port 8000 --reload`).

**Run both at the same time** by opening two terminals, activating the virtual environment in each, and using different ports as in the table. This is useful for comparing them. Both have the same test accounts (`student@th-deg.de` / `test123`, `admin@th-deg.de` / `admin123`).

**First start of the real API:** it creates `team5.db` and adds the two test accounts. To reset it, stop the server and delete `team5.db`.

**Switching between them in your own code:** only the address changes (port 8001 for the mock, port 8000 for the real one). Keep the base URL in one place, such as a setting or environment variable.

**To stop either one:** click its terminal and press `Ctrl + C`.

---

## What changes in the real version

The URLs, JSON fields, status codes and role names stay **the same**. What changes is how it works inside:

| | Mock (`mock_api.py`) | Real (`app/`) |
|---|---|---|
| **Users** | Two fixed test users in memory | A database table (SQLite to start) that persists |
| **Data after restart** | Reset to the two test users | Kept |
| **Passwords** | Plain text, compared directly | Hashed with bcrypt, never stored in plain text |
| **Tokens** | Fake, guessable (`mock-token-<id>`) | Signed JWT with the user ID, role and an 8-hour expiry |
| **Role checks** | Read from the fake user | Read from the verified token and the database |
| **GDPR export** | Empty placeholder keys | The profile plus data from every team that registered an export function |
| **GDPR delete** | Removes the mock user only | Calls every team's delete function first, then removes the user |
| **Secret key** | None | `TEAM5_SECRET` setting, which must be set to a long random value for real use |

**What your code must not rely on in the mock:** the token format, plain-text passwords, and the placeholder export keys.

### Still to be built

- Account creation (registration or university-login import). For now users come only from the test accounts.
- Extra profile fields, once Teams 2 and 3 say which they need.
- An **Authorize** button on `/docs` so tokens work in the browser.
- The shared UI design system (v0.1).
- The other teams' GDPR export and delete functions, agreed and registered.

---

## Using the Python library instead of HTTP

If your code runs in Python in the same environment, you can import our helper functions:

```python
from identity_lib import verify_token, get_user

verify_token(token)   # {"user_id": 3, "role": "student"}, or None if invalid or expired
get_user(3)           # {"user_id": 3, "name": ..., "email": ..., "role": ...}, or None
```
This works with the real service only, not the mock.

---

## Run the tests

```
pytest
```
All tests should pass. They cover login, roles, GDPR, the library and the mock.

## Project layout

```
mock_api.py        Fake API (same URLs and fields as the real one)
app/               The real service
  main.py            Entry point, test-user seeding
  database.py        Database connection
  models.py          Database tables
  schemas.py         API request/response shapes
  auth.py            Passwords, tokens, role checks
  gdpr_hooks.py      Where teams register export/delete functions
  routes/            login.py, users.py, gdpr.py
identity_lib/      Functions other teams can import
tests/             Automatic tests (pytest)
requirements.txt   Packages to install
pytest.ini         Test settings
```

## Working in the team

- Don't commit straight to `main`. Make a branch (`git checkout -b feature/<name>`), push it, and open a pull request.
- Run `pytest` before every push.
- Run `git pull` before you start work.
- Never commit secrets or the `.db` file (`.gitignore` already skips the database).

## Contact

Questions about a URL or a missing field: open an issue in this repo or ask Team 5.
