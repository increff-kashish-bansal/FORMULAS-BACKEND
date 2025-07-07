from fastapi import FastAPI, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import shutil
import uuid

from utils.file_validation import validate_uploaded_file, InvalidFileTypeError, FileTooLargeError

TEMP_DIR = "./temp_uploads"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    os.makedirs(TEMP_DIR, exist_ok=True)
    yield
    # Shutdown logic
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

app = FastAPI(lifespan=lifespan)

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    if file.filename is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name not provided.")

    try:
        # Generate a unique filename to store temporarily
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        temp_file_path = os.path.join(TEMP_DIR, unique_filename)

        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Validate the uploaded file
        validate_uploaded_file(file.filename, temp_file_path)
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "message": "File uploaded and validated successfully",
            "filename": file.filename,
            "temp_path": temp_file_path # In a real app, this would be a reference or ID
        })
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except FileTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        # Log unexpected errors for debugging
        print(f"An unexpected error occurred during file upload: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
    finally:
        # Clean up the temporary file if it was created
        # Check if temp_file_path was successfully assigned before trying to remove
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path) 