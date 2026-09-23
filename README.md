# AI Resume Analyzer

A full-stack resume screening application built with:
- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: FastAPI
- Database: PostgreSQL (SQLite fallback for easy local demo)
- Auth: JWT + bcrypt/passlib
- Resume parsing: PyMuPDF + python-docx
- Matching: weighted skill + semantic similarity using Sentence Transformers

## Features
- Admin registration/login
- JWT-protected APIs
- Admin-isolated data
- Create/update/delete job roles
- Upload PDF/DOCX resumes
- Extract resume text and skills
- Compare every resume against the admin's job roles
- Match percentage, matched skills, missing skills
- Resume analysis history
- Dashboard statistics
- Responsive UI

## Run locally

### 1. Backend
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The app defaults to SQLite (`resume_analyzer.db`) so it runs immediately. For PostgreSQL set:
```bash
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/resume_analyzer
SECRET_KEY=replace-with-a-long-random-secret
```

### Docker (PostgreSQL)
```bash
docker compose up --build
```
Then open http://127.0.0.1:8000/. The app waits for PostgreSQL to be healthy before starting.

### 2. Frontend
The backend serves the frontend at:
http://127.0.0.1:8000/

You can also use a static server, but serving through FastAPI is simplest.

### Demo flow
1. Register an admin (you are redirected to the login page on success).
2. Login.
3. Add several job roles with required/preferred skills.
4. Upload a PDF/DOCX resume.
5. Open Analysis/History to see ranked roles, score, matched and missing skills.

## Notes
The first use of Sentence Transformers may download a model. If model download is unavailable, the app automatically falls back to the deterministic skill/keyword matcher.

For production:
- use PostgreSQL
- use a strong SECRET_KEY
- store uploaded files in S3/object storage
- use HTTPS
- configure CORS for the deployed frontend
- add virus/malware scanning and stricter file validation
- move long AI analysis to a background job queue
