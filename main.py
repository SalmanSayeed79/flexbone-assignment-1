from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from ocr_service import OCRService
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OCR API", 
    description="API to extract text from images using Google Cloud Vision",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_BATCH_SIZE = 20
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png')

# Initialize OCR Service
ocr_service = OCRService()

# Pydantic Models
class OCRResponse(BaseModel):
    text: str
    confidence: float = 0.0
    metadata: dict = None
    message: str = None

class ErrorResponse(BaseModel):
    detail: str

class BatchOCRResult(OCRResponse):
    filename: str

class BatchOCRResponse(BaseModel):
    results: list[BatchOCRResult]
    total_processed: int
    successful_processed: int

def validate_image(file: UploadFile):
    """
    Helper function to validate an image file.
    """
    # Validate MIME type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File {file.filename} is not an image.")

    # Validate file extension
    if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
         raise HTTPException(
             status_code=400, 
             detail=f"File {file.filename}: Only {', '.join(SUPPORTED_EXTENSIONS)} images are supported."
         )

    # Validate file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File {file.filename} too large. Maximum size allowed is {MAX_FILE_SIZE // (1024 * 1024)}MB."
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail=f"File {file.filename} is empty.")

async def validate_image_file(file: UploadFile = File(...)):
    """
    Dependency to validate the uploaded image file.
    """
    validate_image(file)
    return file

@app.get("/", tags=["UI"])
@app.get("/index.html", tags=["UI"])
def read_root():
    return FileResponse("index.html")

@app.post(
    "/ocr", 
    response_model=OCRResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["OCR"]
)
async def perform_ocr(file: UploadFile = Depends(validate_image_file)):
    """
    Accepts an image file and returns the extracted text and confidence score.
    - **file**: JPG/JPEG image file (max 5MB)
    """
    try:
        content = await file.read()
        result = ocr_service.extract_text(content)

        if not result["text"]:
            return OCRResponse(
                text="", 
                confidence=0.0,
                message="No text found in the image."
            )

        return OCRResponse(
            text=result["text"],
            confidence=result["confidence"],
            metadata=result.get("metadata")
        )

    except Exception as e:
        # In a real production app, you might want to log this error instead of returning it directly
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")

@app.post(
    "/ocr-batch", 
    response_model=BatchOCRResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["OCR"]
)
async def perform_batch_ocr(files: list[UploadFile] = File(...)):
    """
    Accepts multiple image files and returns the extracted text and metadata for each.
    Maximum of 20 images per batch.
    """
    if len(files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum batch size is {MAX_BATCH_SIZE} images."
        )
    
    results = []
    successful_count = 0
    
    for file in files:
        try:
            # Validate each file
            validate_image(file)
            
            content = await file.read()
            ocr_result = ocr_service.extract_text(content)
            
            batch_result = BatchOCRResult(
                filename=file.filename,
                text=ocr_result["text"],
                confidence=ocr_result["confidence"],
                metadata=ocr_result.get("metadata"),
                message="Success" if ocr_result["text"] else "No text found"
            )
            results.append(batch_result)
            successful_count += 1
            
        except HTTPException as e:
            # For batch processing, we might want to continue even if one file fails validation
            # But let's follow the standard and return a result with an error message or just append to results
            results.append(BatchOCRResult(
                filename=file.filename,
                text="",
                confidence=0.0,
                message=f"Validation error: {e.detail}"
            ))
        except Exception as e:
            results.append(BatchOCRResult(
                filename=file.filename,
                text="",
                confidence=0.0,
                message=f"Error: {str(e)}"
            ))

    return BatchOCRResponse(
        results=results,
        total_processed=len(files),
        successful_processed=successful_count
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
