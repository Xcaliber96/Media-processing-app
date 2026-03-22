from fastapi import FastAPI, HTTPException, BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests, subprocess, uuid, os, uvicorn


Media_dir, Temp_dir = "media", "temp"
os.makedirs(Media_dir, exist_ok=True)
os.makedirs(Temp_dir, exist_ok=True)

app = FastAPI()
app.mount("/media", StaticFiles(directory=Media_dir), name="media")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class processRequest(BaseModel):
    url: str
    operation: str

def run_ffmpeg(input_path: str, operation: str) -> str:
    output_filename = str(uuid.uuid4())
    if operation == "thumbnail":
        output_path = os.path.join(Media_dir, f"{output_filename}.jpg")
        command = ["ffmpeg", "-y", "-i", input_path, "-ss", "00:00:02", "-vframes", "1", output_path]
    elif operation == "compress":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp4")
        command = ["ffmpeg", "-y", "-i", input_path, "-vcodec", "libx264", "-crf", "28", output_path]
    elif operation == "extract_audio":
        output_path = os.path.join(Media_dir, f"{output_filename}.mp3")
        command = ["ffmpeg", "-y", "-i", input_path, "-map", "0:a?", "-codec:a", "libmp3lame", output_path]
    else:
        raise ValueError("Invalid operation")

    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise Exception(f"FFmpeg error: {result.stderr}")
    return output_path

def download_file(url: str) -> str:
    ext = url.split('.')[-1].split('?')[0].lower()
    if len(ext) > 4 or not ext: ext = "mp4"
    file_path = os.path.join(Temp_dir, f"{uuid.uuid4()}.{ext}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*"
    }
    try:
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        return file_path
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "API is live"}

@app.post("/process")
def process_media(request: processRequest): 
    input_file = None
    try:
        input_file = download_file(request.url)
        output_file = run_ffmpeg(input_file, request.operation)
        
     
        if os.path.exists(input_file): os.remove(input_file)

        BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip('/')
        file_url = f"{BASE_URL}/media/{os.path.basename(output_file)}"
        
        return {"status": "success", "output_url": file_url}
    except Exception as e:
        if input_file and os.path.exists(input_file): os.remove(input_file)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))