from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, field_validator

from resume_parser import (
    extract_text,
    UnsupportedFileTypeError,
    EmptyResumeError,
)

from resume_analyzer import analyze_resume

from job_analyzer import (
    analyze_job_description,
    match_resume_to_job,
)

from interview_generator import generate_interview_questions
from interview_evaluator import evaluate_interview_answer
from interview_summary import generate_interview_summary
from skill_gap_analyzer import analyze_skill_gaps
from career_recommender import generate_skill_recommendations
from cover_letter_generator import create_cover_letter
from resume_quality_analyzer import analyze_resume_quality


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="CareerLens AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


class JobAnalyzeRequest(BaseModel):
    job_description: str
    resume_data: dict

    @field_validator("job_description")
    @classmethod
    def job_description_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("job_description must not be empty.")
        return value

    @field_validator("resume_data")
    @classmethod
    def resume_data_must_not_be_empty(cls, value: dict) -> dict:
        if not isinstance(value, dict) or not value:
            raise ValueError("resume_data must be a non-empty object.")
        return value


class InterviewQuestionsRequest(BaseModel):
    job_data: dict
    resume_data: dict

    @field_validator("job_data")
    @classmethod
    def job_data_must_not_be_empty(cls, value: dict) -> dict:
        if not isinstance(value, dict) or not value:
            raise ValueError("job_data must be a non-empty object.")
        return value

    @field_validator("resume_data")
    @classmethod
    def resume_data_must_not_be_empty(cls, value: dict) -> dict:
        if not isinstance(value, dict) or not value:
            raise ValueError("resume_data must be a non-empty object.")
        return value


class InterviewEvaluateRequest(BaseModel):
    question: dict
    answer: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: dict) -> dict:
        if not isinstance(value, dict) or not value:
            raise ValueError("question must be a non-empty object.")
        return value


class InterviewSummaryRequest(BaseModel):
    evaluations: list[dict]

    @field_validator("evaluations")
    @classmethod
    def evaluations_must_be_valid_list(cls, value: list[dict]) -> list[dict]:
        if not isinstance(value, list):
            raise ValueError("evaluations must be a list.")
        return value


class SkillGapAnalysisRequest(BaseModel):
    resume_data: dict
    job_data: dict

    @field_validator("resume_data")
    @classmethod
    def resume_data_must_be_object(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValueError("resume_data must be an object.")
        return value

    @field_validator("job_data")
    @classmethod
    def job_data_must_be_object(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValueError("job_data must be an object.")
        return value


class CareerRecommendationsRequest(BaseModel):
    skill_gaps: list[dict]

    @field_validator("skill_gaps")
    @classmethod
    def skill_gaps_must_be_valid_list(cls, value: list[dict]) -> list[dict]:
        if not isinstance(value, list):
            raise ValueError("skill_gaps must be a list.")
        return value


class CoverLetterRequest(BaseModel):
    resume_data: dict
    job_data: dict

    @field_validator("resume_data")
    @classmethod
    def resume_data_must_be_object(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValueError("resume_data must be an object.")
        return value

    @field_validator("job_data")
    @classmethod
    def job_data_must_be_object(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValueError("job_data must be an object.")
        return value


class SemanticRelevanceRequest(BaseModel):
    job_requirement: str
    resume_context: str

    @field_validator('job_requirement')
    @classmethod
    def check_job_req(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('job_requirement cannot be empty')
        return v
        
    @field_validator('resume_context')
    @classmethod
    def check_resume_ctx(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('resume_context cannot be empty')
        return v

class ResumeQualityRequest(BaseModel):
    resume_data: dict

    @field_validator("resume_data")
    @classmethod
    def resume_data_must_be_object(cls, value: dict) -> dict:
        if not isinstance(value, dict):
            raise ValueError("resume_data must be an object.")
        return value


@app.get("/")
def root():
    return {
        "message": "CareerLens AI API is running!"
    }


@app.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):

    # Check file extension
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf and .docx files are supported.",
        )

    # Read uploaded file
    file_bytes = await file.read()

    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB.",
        )

    # Check empty file
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Extract resume text
    try:
        extracted_text = extract_text(
            file.filename,
            file_bytes,
        )

    except UnsupportedFileTypeError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except EmptyResumeError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not process this file. It may be corrupted.",
        )

    # Analyze extracted resume text
    resume_data = analyze_resume(extracted_text)

    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "resume_data": resume_data,
        "character_count": len(extracted_text),
    }


@app.post("/job/analyze")
async def analyze_job(request: JobAnalyzeRequest):

    # Analyze job description
    job_data = analyze_job_description(
        request.job_description
    )

    # Match resume against analyzed job
    match_result = match_resume_to_job(
        request.resume_data,
        job_data,
    )

    transferable_evidence = []
    try:
        from ml.job_transferable_evidence import analyze_job_transferable_evidence
        missing_skills = match_result.get("missing_skills", [])
        transferable_evidence = analyze_job_transferable_evidence(missing_skills, request.resume_data)
    except Exception as e:
        print(f"Failed to analyze transferable evidence: {e}")

    return {
        "job": job_data,
        "match": match_result,
        "transferable_evidence": transferable_evidence
    }


@app.post("/job/analyze-upload")
async def analyze_job_upload(
    file: UploadFile = File(...),
    resume_data: str = Form(...)
):
    import json
    try:
        resume_data_dict = json.loads(resume_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid resume_data JSON")

    # Check file extension
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only .pdf and .docx files are supported.",
        )

    # Read uploaded file
    file_bytes = await file.read()

    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB.",
        )

    # Check empty file
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # Extract text
    try:
        extracted_text = extract_text(
            file.filename,
            file_bytes,
        )
    except UnsupportedFileTypeError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except EmptyResumeError:
        raise HTTPException(
            status_code=422,
            detail="This file does not contain readable text. Please upload a text-based job description file or paste the job description manually.",
        )
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not process this file. It may be corrupted.",
        )

    # Analyze job description
    job_data = analyze_job_description(extracted_text)

    # Match resume against analyzed job
    match_result = match_resume_to_job(
        resume_data_dict,
        job_data,
    )

    transferable_evidence = []
    try:
        from ml.job_transferable_evidence import analyze_job_transferable_evidence
        missing_skills = match_result.get("missing_skills", [])
        transferable_evidence = analyze_job_transferable_evidence(missing_skills, resume_data_dict)
    except Exception as e:
        print(f"Failed to analyze transferable evidence: {e}")

    return {
        "job": job_data,
        "match": match_result,
        "transferable_evidence": transferable_evidence,
        "extracted_text": extracted_text,
    }


@app.post("/interview/questions")
async def generate_questions(request: InterviewQuestionsRequest):
    
    # Generate interview questions
    questions = generate_interview_questions(
        request.job_data,
        request.resume_data,
    )
    
    return {
        "questions": questions
    }


@app.post("/interview/evaluate")
async def evaluate_answer(request: InterviewEvaluateRequest):
    
    # Evaluate the answer
    evaluation = evaluate_interview_answer(
        request.question,
        request.answer,
    )
    
    return {
        "evaluation": evaluation
    }


@app.post("/interview/summary")
async def generate_summary(request: InterviewSummaryRequest):
    
    # Generate the interview session summary
    summary = generate_interview_summary(
        request.evaluations
    )
    
    return {
        "summary": summary
    }


@app.post("/skills/gap-analysis")
async def analyze_skill_gaps_endpoint(request: SkillGapAnalysisRequest):
    
    analysis = analyze_skill_gaps(
        request.resume_data,
        request.job_data
    )
    
    return analysis


@app.post("/career/recommendations")
async def get_career_recommendations(request: CareerRecommendationsRequest):
    
    result = generate_skill_recommendations(
        request.skill_gaps
    )
    
    return result


@app.post("/cover-letter/generate")
async def generate_cover_letter_endpoint(request: CoverLetterRequest):
    
    result = create_cover_letter(
        request.resume_data,
        request.job_data
    )
    
    return result


@app.post("/resume/quality")
async def analyze_resume_quality_endpoint(request: ResumeQualityRequest):
    
    result = analyze_resume_quality(
        request.resume_data
    )
    
    return result
@app.post("/ml/relevance")
async def analyze_semantic_relevance(request: SemanticRelevanceRequest):
    try:
        from ml.relevance_api import analyze_relevance
        result = analyze_relevance(request.job_requirement, request.resume_context)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze semantic relevance."
        )

