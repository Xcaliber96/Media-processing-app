from fastapi import FastAPI
from pydantic import BaseModel

import requests
import uuid 
import os



app = FastAPI()

class processRequest(BaseModel):
    url: str
    operation: str  

Temp_dir = "temp"

def download_file(url: str) -> str:
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
    
    allowerd_operations = ["thumbnail", "compress", "extract_audio"]
    if request.operation not in allowerd_operations:
        return{
            "status" : "error",
            "message" : f"Invalid operation"
        }
    try:
        file_path = download_file(request.url)
        
        return {
            "status": "success",
            "message": f"File downloaded and processed successfully. Operation: {request.operation}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }