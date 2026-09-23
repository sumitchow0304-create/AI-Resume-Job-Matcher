from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from ..config import settings
from ..database import get_db
from ..models import Admin, Resume
from ..schemas import ResumeOut
from ..utils.security import get_current_admin
from ..services.resume_parser import extract_text

router = APIRouter(prefix="/api/resumes", tags=["Resumes"])
MAX_SIZE = 10 * 1024 * 1024
ALLOWED = {".pdf", ".docx"}

@router.post("/upload", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...), admin: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, "Only PDF and DOCX files are allowed")
    content = await file.read()
    if not content:
        raise HTTPException(400, "The uploaded file is empty")
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "File is larger than 10 MB")

    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    stored = f"{admin.id}_{uuid4().hex}{ext}"
    path = str(Path(settings.UPLOAD_DIR) / stored)
    Path(path).write_bytes(content)

    try:
        text = extract_text(path)
    except Exception:
        Path(path).unlink(missing_ok=True)
        raise HTTPException(400, "Could not parse the uploaded resume")
    if not text.strip():
        # Typically a scanned/image-only PDF: there is nothing to analyze.
        Path(path).unlink(missing_ok=True)
        raise HTTPException(400, "No readable text found in this file (scanned/image-only PDFs are not supported)")

    resume = Resume(
        admin_id=admin.id,
        original_filename=Path(file.filename).name[:255],
        stored_filename=stored,
        file_path=path,
        extracted_text=text[:100000],
    )
    db.add(resume); db.commit(); db.refresh(resume)
    return resume

@router.get("", response_model=list[ResumeOut])
def list_resumes(admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.admin_id == admin.id).order_by(Resume.id.desc()).all()

@router.delete("/{resume_id}")
def delete_resume(resume_id: int, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or resume.admin_id != admin.id:
        raise HTTPException(404, "Resume not found")
    Path(resume.file_path).unlink(missing_ok=True)
    db.delete(resume); db.commit()
    return {"message": "Deleted"}
