from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException 
from fastapi.staticfiles import StaticFiles  
from fastapi.middleware.cors import CORSMiddleware

import requests
import subprocess
import uuid 
import os


app = FastAPI()
app.mount("/media", StaticFiles(directory="media"), name="media")

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

Media_dir = "media"
Temp_dir = "temp"

def run_ffmpeg(input_path: str, operation: str) -> str:
    os.makedirs(Media_dir, exist_ok=True)

    output_filename = str(uuid.uuid4())

    if operation == "thumbnail":
        output_path = os.path.join(Media_dir, f"{output_filename}.jpg")
        command = [
            "ffmpeg",
            "-i", input_path,
            "-ss", "00:00:02",
            "-vframes", "1",
            output_path
        ]

    elif operation == "compress":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp4")
        command = [
            "ffmpeg", "-i", input_path,
            "-vcodec", "libx264",
            "-crf", "28",
            output_path
        ]

    elif operation == "extract_audio":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp3")
        command = [
            "ffmpeg",
            "-i", input_path,
            "-map", "0:a:0",
            "-codec:a", "libmp3lame",
            output_path
        ]
    else:
        raise ValueError("Invalid operation")

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60
    )

    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr.decode()}")

    return output_path


def download_file(url: str) -> str:
    os.makedirs(Temp_dir, exist_ok=True)
    try:
        filename = f"{uuid.uuid4()}.mp4"
        file_path = os.path.join(Temp_dir, filename)
        response = requests.get(url, stream=True, timeout=10)

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
    return {"Hello": "World"}

@app.post("/process")
def process_media(request: processRequest): 
    
    allowed_operations = ["thumbnail", "compress", "extract_audio"]
    if request.operation not in allowed_operations:
        raise HTTPException(status_code=400, detail=f"Invalid operation. Allowed operations: {', '.join(allowerd_operations)}")
    try:
        input_file = download_file(request.url)

        output_file = run_ffmpeg(input_file, request.operation)

        output_file = output_file.replace("\\", "/")
        file_url = f"http://127.0.0.1:8000/{output_file}"

        return {
            "status": "success",
            "output_url": file_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))