from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin, JobRole
from ..schemas import JobCreate, JobOut
from ..utils.security import get_current_admin

router = APIRouter(prefix="/api/jobs", tags=["Job Roles"])

def own(job_id: int, admin: Admin, db: Session):
    job = db.get(JobRole, job_id)
    if not job or job.admin_id != admin.id:
        raise HTTPException(404, "Job role not found")
    return job

@router.get("", response_model=list[JobOut])
def list_jobs(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(JobRole).filter(JobRole.admin_id == admin.id).order_by(JobRole.id.desc()).all()

@router.post("", response_model=JobOut)
def create_job(data: JobCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    job = JobRole(admin_id=admin.id, **data.model_dump())
    db.add(job); db.commit(); db.refresh(job)
    return job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, data: JobCreate, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    job = own(job_id, admin, db)
    for k, v in data.model_dump().items():
        setattr(job, k, v)
    db.commit(); db.refresh(job)
    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    job = own(job_id, admin, db)
    db.delete(job); db.commit()
    return {"message": "Deleted"}
