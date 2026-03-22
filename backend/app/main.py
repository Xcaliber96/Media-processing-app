from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException 
from fastapi.staticfiles import StaticFiles  
from fastapi.middleware.cors import CORSMiddleware

import requests
import subprocess
import uuid 
import os
import uvicorn 


Media_dir = "media"
Temp_dir = "temp"
os.makedirs(Media_dir, exist_ok=True)
os.makedirs(Temp_dir, exist_ok=True)

app = FastAPI()
app.mount("/media", StaticFiles(directory=Media_dir), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class processRequest(BaseModel):
    url: str
    operation: str  

def run_ffmpeg(input_path: str, operation: str) -> str:
    output_filename = str(uuid.uuid4())

    if operation == "thumbnail":
        output_path = os.path.join(Media_dir, f"{output_filename}.jpg")
        command = [
            "ffmpeg", 
            "-y",  
            "-i", input_path,
            "-ss", "00:00:02",
            "-vframes", "1",
            output_path
        ]

    elif operation == "compress":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp4")
        command = [
            "ffmpeg", 
            "-y",
            "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            output_path
        ]

    elif operation == "extract_audio":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp3")
        command = [
            "ffmpeg", 
            "-y",
            "-i", input_path,
            "-map", "0:a?", 
            "-codec:a", "libmp3lame",
            output_path
        ]
    else:
        raise ValueError("Invalid operation")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180 
    )

    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode()}")

    return output_path

def download_file(url: str) -> str:
    try:
        filename = f"{uuid.uuid4()}.mp4"
        file_path = os.path.join(Temp_dir, filename)
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*",
        }
        response = requests.get(url, stream=True, timeout=10, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to download file: {response.status_code}")
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024*1024):
                if chunk:
                    file.write(chunk)
        return file_path
    
    except Exception as e:
        raise Exception(f"Failed to download file: {e}")
    
@app.get("/")
def read_root():
    return {"status": "API is live and ready"}

@app.post("/process")
def process_media(request: processRequest): 
    
    allowed_operations = ["thumbnail", "compress", "extract_audio"]
    if request.operation not in allowed_operations:
        raise HTTPException(status_code=400, detail=f"Invalid operation. Allowed operations: {', '.join(allowed_operations)}")
    
    
    print(f"Processing: {request.operation} for URL: {request.url}")

    try:
        input_file = download_file(request.url)
        output_file = run_ffmpeg(input_file, request.operation)

        if os.path.exists(input_file):
            os.remove(input_file)

        output_file = output_file.replace("\\", "/")
        BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
        
        file_url = f"{BASE_URL}/media/{os.path.basename(output_file)}"
        print(f"Success! File available at: {file_url}")

        return {
            "status": "success",
            "output_url": file_url
        }
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)