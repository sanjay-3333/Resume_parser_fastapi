# models.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Parsed fields
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[str] = None
    jobTitle: Optional[str] = None
    education: Optional[str] = None
    educationHistory: Optional[str] = None
    skills: Optional[str] = None
    languages: Optional[str] = None
    expectedSalary: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    fullAddress: Optional[str] = None
    profileDescription: Optional[str] = None
    yearsOfExp: Optional[str] = None

    # Socials
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    socials: Optional[str] = None  # (unused legacy; keep for backward compatibility)

    # Cloudinary
    public_id: Optional[str] = None            # <-- store Cloudinary public_id
    cv_url: Optional[str] = None               # secure_url (uploaded asset)
    cv_download_url: Optional[str] = None      # browser download helper
    socials: Optional[str] 
    # Audit / reporting
    uploader_ip: Optional[str] = None
    projectSummary: Optional[str] = None
