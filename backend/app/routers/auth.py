from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin
from ..schemas import AdminRegister, AdminLogin, Token, AdminOut
from ..utils.security import hash_password, verify_password, create_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=AdminOut)
def register(data: AdminRegister, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(Admin).filter(Admin.email == email).first():
        raise HTTPException(400, "Email already registered")
    admin = Admin(name=data.name.strip(), email=email, password_hash=hash_password(data.password))
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@router.post("/login", response_model=Token)
def login(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == data.email.strip().lower()).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return Token(access_token=create_token(admin.id))

@router.get("/me", response_model=AdminOut)
def me(admin: Admin = Depends(get_current_admin)):
    return admin
