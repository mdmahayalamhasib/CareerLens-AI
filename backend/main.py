from fastapi import FastAPI, UploadFile, File, HTTPException

from resume_parser import (
    extract_text,
    UnsupportedFileTypeError,
    EmptyResumeError,
)


app = FastAPI(title="CareerLens AI")


MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


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

    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "character_count": len(extracted_text),
    }