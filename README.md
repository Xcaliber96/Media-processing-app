#  Media Processing App

A full-stack media processing application that allows users to submit a media URL, perform operations using FFmpeg, and view/download the processed output through a clean web interface.

---

##  Features

-  Extract thumbnail from video  
-  Compress video to reduce size  
-  Extract audio from video  
-  Real-time processing using FFmpeg (via subprocess)  
-  Interactive frontend with React + Tailwind CSS  
-  Public URL generation for processed files  

---

##  How It Works

1. User enters a media URL and selects an operation  
2. Frontend sends a request to the backend API  
3. Backend downloads the media file  
4. FFmpeg processes the file using subprocess  
5. Processed file is stored and served via a public URL  
6. Frontend displays the result (image/video/audio)  

---

##  Tech Stack

**Backend**
- FastAPI (Python)
- FFmpeg (subprocess)
- Requests

**Frontend**
- React (Vite)
- Tailwind CSS
- Axios

---

## Project Structure
media-processing-app/
│
├── backend/
│ ├── app/
│ │ └── main.py
│ ├── media/
│ ├── temp/
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ └── package.json
│
└── README.md