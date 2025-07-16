from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, select, create_engine
from models import Resume
from parser import parse_resume_from_path
import os
import shutil
import json
from typing import List
from fpdf import FPDF

# -------------------------
# Helper to sanitize unicode text for PDF
def sanitize(text):
    if not text:
        return "N/A"
    return text.encode("latin-1", "replace").decode("latin-1")

# -------------------------
# FastAPI app setup
app = FastAPI()

# -------------------------
# Database setup
DATABASE_URL = "sqlite:///resumes.db"
engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)

# -------------------------
# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# -------------------------
# Route: Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# -------------------------
# Route: View all parsed resumes
@app.get("/resumes", response_class=HTMLResponse)
def view_resumes(request: Request):
    with Session(engine) as session:
        resumes: List[Resume] = session.exec(select(Resume)).all()
        return templates.TemplateResponse("resumes.html", {"request": request, "resumes": resumes})

# -------------------------
# Route: Upload and parse resume
@app.post("/upload", response_class=HTMLResponse)
async def upload_resume(request: Request, resume: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, resume.filename)

        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

        # Parse resume data
        data = parse_resume_from_path(file_path)

        # Save to database
        with Session(engine) as session:
            resume_record = Resume(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                age=data["age"],
                city=data["city"],
                country=data["country"],
                fullAddress=data["fullAddress"],
                jobTitle=data["jobTitle"],
                profileDescription=data["profileDescription"],
                education=data["education"],
                yearsOfExp=data["yearsOfExp"],
                languages=", ".join(data["languages"]) if data.get("languages") else "",
                skills=", ".join(data["skills"]) if data.get("skills") else "",
                expectedSalary=data["expectedSalary"],
                educationHistory="\n".join(data["educationHistory"]),
                linkedin=data["socials"].get("linkedin", ""),
                github=data["socials"].get("github", ""),
                portfolio=data["socials"].get("portfolio", "")
            )
            session.add(resume_record)
            session.commit()

        os.remove(file_path)

        return templates.TemplateResponse("index.html", {
            "request": request,
            "parsed": data,
            "pdf_url": "/download"
        })

    except Exception as e:
        import traceback
        print("❌ Error during /upload:", traceback.format_exc())
        return PlainTextResponse("Internal Server Error: " + str(e), status_code=500)

# -------------------------
# Route: Generate and return PDF
@app.get("/download")
async def download_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    with Session(engine) as session:
        resume = session.exec(select(Resume).order_by(Resume.id.desc())).first()
        if not resume:
            return PlainTextResponse("No resume data found.", status_code=404)

        # Resume Header
        pdf.cell(200, 10, txt="AI Resume Parser Result", ln=True, align='C')
        pdf.ln(10)

        # Resume Fields
        pdf.multi_cell(0, 10, sanitize(f"Name: {resume.name}"))
        pdf.multi_cell(0, 10, sanitize(f"Email: {resume.email}"))
        pdf.multi_cell(0, 10, sanitize(f"Phone: {resume.phone}"))
        pdf.multi_cell(0, 10, sanitize(f"Job Title: {resume.jobTitle}"))
        pdf.multi_cell(0, 10, sanitize(f"Age: {resume.age or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Location: {resume.fullAddress or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Languages: {resume.languages or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Skills: {resume.skills or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Expected Salary: {resume.expectedSalary or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Education Summary: {resume.education or 'N/A'}"))

        # Education History
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Education History", ln=True)
        pdf.set_font("Arial", size=12)
        for edu in resume.educationHistory.split("\n"):
            pdf.multi_cell(0, 10, sanitize(edu))

        # Social Links
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(200, 10, txt="Social Links", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, sanitize(f"LinkedIn: {resume.linkedin or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"GitHub: {resume.github or 'N/A'}"))
        pdf.multi_cell(0, 10, sanitize(f"Portfolio: {resume.portfolio or 'N/A'}"))

        # Save to file
        output_path = "output_resume.pdf"
        pdf.output(output_path)

    return FileResponse(path=output_path, filename="resume_output.pdf", media_type='application/pdf')
