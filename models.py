from sqlmodel import SQLModel, Field
from typing import Optional

class Resume(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    age: Optional[str]
    jobTitle: Optional[str]
    education: Optional[str]
    educationHistory: Optional[str]
    skills: Optional[str]
    languages: Optional[str]
    expectedSalary: Optional[str]
    city: Optional[str]
    country: Optional[str]
    fullAddress: Optional[str]
    linkedin: Optional[str]
    github: Optional[str]
    portfolio: Optional[str]
    socials: Optional[str]
    cv_url: Optional[str]            # Cloudinary resume link
    projectSummary: Optional[str] 