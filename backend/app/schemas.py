import re
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _clean_email(v: str) -> str:
    v = (v or "").strip().lower()
    if not EMAIL_RE.match(v):
        raise ValueError("Enter a valid email address")
    return v

class AdminRegister(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(max_length=255)
    password: str = Field(min_length=6, max_length=128)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("email")
    @classmethod
    def valid_email(cls, v):
        return _clean_email(v)

    @field_validator("password")
    @classmethod
    def bcrypt_limit(cls, v):
        # bcrypt only uses the first 72 bytes; reject longer passwords instead of silently truncating.
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes long")
        return v

class AdminLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminOut(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    required_skills: str = ""
    preferred_skills: str = ""
    minimum_experience: float = Field(default=0, ge=0, le=60)
    education: str = Field(default="", max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        return v.strip() if isinstance(v, str) else v

class JobOut(JobCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AnalysisOut(BaseModel):
    id: int
    job_role_id: int
    job_title: str
    match_percentage: float
    semantic_score: float
    skill_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str

class ResumeOut(BaseModel):
    id: int
    original_filename: str
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)
