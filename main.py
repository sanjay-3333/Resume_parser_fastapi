import os
import shutil
import mimetypes
from typing import List, Any, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqlmodel import SQLModel, Session, select, create_engine
from sqlalchemy import func as sa_func
from starlette.concurrency import run_in_threadpool
from fpdf import FPDF
from dotenv import load_dotenv
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload

from models import Resume
from parser import parse_resume_from_path

# ------------------------------------------------------------------
# Load environment variables
# ------------------------------------------------------------------
load_dotenv()
CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
API_KEY = os.getenv("CLOUDINARY_API_KEY")
API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not all([CLOUD_NAME, API_KEY, API_SECRET]):
    raise RuntimeError("Missing Cloudinary credentials in .env")

cloudinary.config(cloud_name=CLOUD_NAME, api_key=API_KEY, api_secret=API_SECRET, secure=True)
print(f"✅ Cloudinary configured for '{CLOUD_NAME}'")

# ------------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------------
app = FastAPI(title="AI Resume Parser", version="1.4.0")

# ------------------------------------------------------------------
# Database setup
# ------------------------------------------------------------------
DATABASE_URL = "sqlite:///resumes.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SQLModel.metadata.create_all(engine)

# ------------------------------------------------------------------
# Static files & Templates
# ------------------------------------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def sanitize(text: Optional[str]) -> str:
    return text.encode("latin-1", "replace").decode("latin-1") if text else "N/A"

def _get(d: Dict[str, Any], k: str, default=""):
    return d.get(k, default) if isinstance(d, dict) else default

def _get_list(d: Dict[str, Any], k: str):
    v = _get(d, k, [])
    return v if isinstance(v, list) else []

def _get_social(d: Dict[str, Any], k: str):
    soc = _get(d, "socials", {})
    return soc.get(k, "") if isinstance(soc, dict) else ""

# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

# ✅ Home Page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "parsed": None,
        "last_resume_id": None
    })

# ✅ View All Resumes
@app.get("/resumes", response_class=HTMLResponse)
def view_resumes(request: Request, page: int = Query(1, ge=1), page_size: int = Query(5, ge=1, le=50)):
    with Session(engine) as session:
        total_count = session.exec(select(sa_func.count(Resume.id))).one()
        offset = (page - 1) * page_size
        resumes: List[Resume] = session.exec(select(Resume).order_by(Resume.id.desc()).offset(offset).limit(page_size)).all()

    total_pages = (total_count + page_size - 1) // page_size
    return templates.TemplateResponse("resumes.html", {
        "request": request,
        "resumes": resumes,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })

# ✅ Upload & Parse Resume
@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, resume: UploadFile = File(...)):
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    local_path = os.path.join(upload_dir, resume.filename)

    try:
        # Save locally
        with open(local_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # Validate file type
        mime_type, _ = mimetypes.guess_type(local_path)
        if mime_type != "application/pdf":
            os.remove(local_path)
            return PlainTextResponse("Please upload a valid PDF file.", status_code=400)

        # Upload to Cloudinary
        client_ip = request.client.host if request.client else "unknown"
        filename_root, _ = os.path.splitext(resume.filename)
        public_id = f"resumes/{client_ip.replace('.', '_')}_{filename_root}"

        upload_result = await run_in_threadpool(cloudinary_upload, local_path, public_id=public_id, resource_type="raw", access_mode="public", overwrite=True)
        secure_url = upload_result["secure_url"]
        download_url = f"{secure_url}?fl_attachment=1"

        # Parse resume
        data = await run_in_threadpool(parse_resume_from_path, local_path)
        if not isinstance(data, dict):
            data = {}

        # Save to DB
        with Session(engine) as session:
            resume_record = Resume(
                name=_get(data, "name"),
                email=_get(data, "email"),
                phone=_get(data, "phone"),
                age=_get(data, "age"),
                city=_get(data, "city"),
                country=_get(data, "country"),
                fullAddress=_get(data, "fullAddress"),
                jobTitle=_get(data, "jobTitle"),
                profileDescription=_get(data, "profileDescription"),
                education=_get(data, "education"),
                yearsOfExp=_get(data, "yearsOfExp"),
                languages=", ".join(_get_list(data, "languages")),
                skills=", ".join(_get_list(data, "skills")),
                expectedSalary=_get(data, "expectedSalary"),
                educationHistory="\n".join(_get_list(data, "educationHistory")),
                linkedin=_get_social(data, "linkedin"),
                github=_get_social(data, "github"),
                portfolio=_get_social(data, "portfolio"),
                cv_url=secure_url,
                cv_download_url=download_url,
                uploader_ip=client_ip,
                public_id=public_id,
                uploaded_at=datetime.utcnow()
            )
            session.add(resume_record)
            session.commit()
            session.refresh(resume_record)
            new_id = resume_record.id

        # Cleanup
        os.remove(local_path)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "parsed": data,
            "last_resume_id": new_id
        })

    except Exception as e:
        if os.path.exists(local_path):
            os.remove(local_path)
        return PlainTextResponse(f"Internal Server Error: {str(e)}", status_code=500)

# ✅ API for Resume Details (for modal)
@app.get("/resume/{resume_id}/details")
async def get_resume_details(resume_id: int):
    with Session(engine) as session:
        resume = session.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    return {
        "name": resume.name,
        "email": resume.email,
        "phone": resume.phone,
        "jobTitle": resume.jobTitle,
        "age": resume.age,
        "fullAddress": resume.fullAddress,
        "city": resume.city,
        "country": resume.country,
        "languages": resume.languages,
        "skills": resume.skills,
        "expectedSalary": resume.expectedSalary,
        "education": resume.education,
        "yearsOfExp": resume.yearsOfExp,
        "educationHistory": resume.educationHistory,
        "linkedin": resume.linkedin,
        "github": resume.github,
        "portfolio": resume.portfolio,
    }

# ✅ Download Parsed Resume by ID
@app.get("/resume/{resume_id}/download")
async def download_parsed_pdf_by_id(resume_id: int):
    with Session(engine) as session:
        resume = session.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return generate_pdf(resume)

# ✅ PDF Generator
def generate_pdf(resume: Resume):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Resume Parser Result", ln=True, align="C")
    pdf.ln(10)

    fields = [
        f"Name: {resume.name}",
        f"Email: {resume.email}",
        f"Phone: {resume.phone}",
        f"Job Title: {resume.jobTitle}",
        f"Age: {resume.age or 'N/A'}",
        f"Location: {resume.fullAddress or 'N/A'}",
        f"Languages: {resume.languages or 'N/A'}",
        f"Skills: {resume.skills or 'N/A'}",
        f"Expected Salary: {resume.expectedSalary or 'N/A'}",
        f"Education: {resume.education or 'N/A'}",
        f"Years of Experience: {resume.yearsOfExp or 'N/A'}",
        f"LinkedIn: {resume.linkedin or 'N/A'}",
        f"GitHub: {resume.github or 'N/A'}",
        f"Portfolio: {resume.portfolio or 'N/A'}",
    ]

    for field in fields:
        pdf.multi_cell(0, 10, sanitize(field))

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Education History", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, sanitize(resume.educationHistory or "N/A"))

    output_path = "output_resume.pdf"
    pdf.output(output_path)
    return FileResponse(path=output_path, filename="parsed_resume.pdf", media_type="application/pdf")
