from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
import uvicorn
from PIL import Image
import io
import os
from datetime import datetime

app = FastAPI(title="Image Background Remover API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
    expose_headers=["Content-Disposition"]  # Important for file downloads
)

# Create uploads and results directories if they don't exist
UPLOAD_DIR = "uploads"
RESULT_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


@app.post("/remove-background/")
async def remove_background(file: UploadFile = File(...)):
    """
    Endpoint to remove background from uploaded image
    Returns the processed image without background
    """
    try:
        # Generate unique filename using timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = file.filename
        filename_without_ext = os.path.splitext(original_filename)[0]

        # Read uploaded image
        contents = await file.read()
        input_image = Image.open(io.BytesIO(contents))

        # Remove background
        output_image = remove(input_image)

        # Save the result
        result_filename = f"{filename_without_ext}_nobg_{timestamp}.png"
        result_path = os.path.join(RESULT_DIR, result_filename)
        output_image.save(result_path, "PNG")

        # Return the processed image
        response = FileResponse(
            result_path,
            media_type="image/png",
            filename=result_filename
        )
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return response

    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Image Background Remover API",
        "usage": "POST an image to /remove-background/ endpoint"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)