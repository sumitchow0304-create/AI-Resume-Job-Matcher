import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin, Resume, JobRole, AnalysisResult
from ..schemas import AnalysisOut
from ..utils.security import get_current_admin
from ..services.matcher import analyze

router = APIRouter(prefix="/api/analysis", tags=["AI Analysis"])

def result_dict(r):
    return {
        "id": r.id,
        "job_role_id": r.job_role_id,
        "job_title": r.job.title,
        "match_percentage": r.match_percentage,
        "semantic_score": r.semantic_score,
        "skill_score": r.skill_score,
        "matched_skills": json.loads(r.matched_skills or "[]"),
        "missing_skills": json.loads(r.missing_skills or "[]"),
        "explanation": r.explanation,
    }

@router.post("/resume/{resume_id}", response_model=list[AnalysisOut])
def analyze_resume(resume_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or resume.admin_id != admin.id:
        raise HTTPException(404, "Resume not found")

    jobs = db.query(JobRole).filter(JobRole.admin_id == admin.id).all()
    if not jobs:
        raise HTTPException(400, "Add at least one job role before analyzing")

    # Replace prior analysis for this resume so history shows the latest evaluation.
    db.query(AnalysisResult).filter(AnalysisResult.resume_id == resume.id).delete()
    results = []
    for job in jobs:
        a = analyze(resume.extracted_text, job)
        row = AnalysisResult(
            resume_id=resume.id,
            job_role_id=job.id,
            match_percentage=a["match_percentage"],
            semantic_score=a["semantic_score"],
            skill_score=a["skill_score"],
            matched_skills=json.dumps(a["matched_skills"]),
            missing_skills=json.dumps(a["missing_skills"]),
            explanation=a["explanation"],
        )
        db.add(row); results.append(row)
    db.commit()
    for r in results: db.refresh(r)
    return [result_dict(r) for r in sorted(results, key=lambda x: x.match_percentage, reverse=True)]

@router.get("/resume/{resume_id}", response_model=list[AnalysisOut])
def get_analysis(resume_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or resume.admin_id != admin.id:
        raise HTTPException(404, "Resume not found")
    rows = db.query(AnalysisResult).filter(AnalysisResult.resume_id == resume_id).all()
    return [result_dict(r) for r in sorted(rows, key=lambda x: x.match_percentage, reverse=True)]
