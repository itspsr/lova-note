from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import uuid
import upload_utils as uu  # Import the function from upload_utils.py
import whisper_utils as wu  # Import functions from whisper_utils.py
from fastapi import HTTPException
from fpdf import FPDF
from docx import Document

app = FastAPI()

# Mount the static folder to serve uploaded files (optional)
app.mount("/static", StaticFiles(directory="static"), name="static")

class TranscriptionResult(BaseModel):
    transcription: str
    success: bool
    shareable_link: str  # Added the shareable link in response

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LovaNote - Cloud Uploader</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #121212;
                color: #fff;
                text-align: center;
                margin: 0;
                padding: 0;
            }
            h1, h2, h3 {
                font-family: 'Helvetica Neue', sans-serif;
                color: #fff;
                margin-bottom: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
                padding: 30px;
            }
            .header {
                background-color: #1F1F1F;
                padding: 50px 0;
                border-radius: 10px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            .button {
                padding: 12px 30px;
                font-size: 16px;
                background-color: #6200EA;
                border: none;
                color: #fff;
                border-radius: 30px;
                cursor: pointer;
                transition: background-color 0.3s;
                text-transform: uppercase;
            }
            .button:hover {
                background-color: #3700B3;
            }
            input[type="file"] {
                display: none;
            }
            .file-input-label {
                display: inline-block;
                background-color: #6200EA;
                color: white;
                padding: 12px 30px;
                border-radius: 30px;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .file-input-label:hover {
                background-color: #3700B3;
            }
            audio {
                width: 80%;
                border-radius: 8px;
                margin-top: 20px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
            }
            #transcriptionResult {
                margin-top: 20px;
                font-size: 18px;
                background-color: #333;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                max-width: 800px;
                margin: 30px auto;
                text-align: left;
                color: #ddd;
            }
            .footer {
                background-color: #1F1F1F;
                padding: 20px;
                margin-top: 50px;
                border-radius: 10px;
                text-align: center;
                font-size: 14px;
                color: #bbb;
            }
            #progressBarContainer {
                margin-top: 20px;
                display: none;
                width: 80%;
                margin: 0 auto;
                background: #444;
                height: 12px;
                border-radius: 6px;
                overflow: hidden;
            }
            #progressBar {
                width: 0%;
                height: 100%;
                background: #03DAC6;
                transition: width 0.3s ease;
            }
            #progressStatus {
                margin-top: 10px;
                font-size: 16px;
                color: #ccc;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>LovaNote Cloud Uploader</h1>
                <h2>Upload Your Audio File for Transcription</h2>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <label for="fileInput" class="file-input-label">Choose an Audio File</label>
                <input type="file" id="fileInput" name="file" accept="audio/*" required onchange="uploadFile()">
            </form>

            <h3>Playback and Transcribe Audio</h3>
            <audio controls id="audioPlayer">
                <source id="audioSource" src="" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>

            <div id="progressBarContainer">
                <div id="progressBar"></div>
            </div>
            <div id="progressStatus"></div>

            <div id="transcriptionResult"></div>
            <button id="transcribeButton" class="button" onclick="transcribe()">Transcribe Audio</button>

            <div class="footer">
                <p>Powered by LovaNote. Transforming audio to text with ease.</p>
            </div>
        </div>

        <script>
            let uploadedFileName = "";

            function uploadFile() {
                const fileInput = document.getElementById('fileInput');
                const file = fileInput.files[0];
                const formData = new FormData();
                formData.append('file', file);

                fetch('/upload/', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.filename) {
                        setAudioFile(data.filename);
                    } else {
                        alert('File upload failed!');
                    }
                })
                .catch(error => {
                    alert('Error uploading file!');
                    console.error(error);
                });
            }

            function setAudioFile(filename) {
                uploadedFileName = filename;
                document.getElementById('audioSource').src = `https://res.cloudinary.com/dunfulrqo/video/upload/${filename}.mp3`;
                const audio = document.querySelector('audio');
                audio.load();
            }

            function simulateProgressBar(callback) {
                let progress = 0;
                const progressBar = document.getElementById('progressBar');
                const container = document.getElementById('progressBarContainer');
                const status = document.getElementById('progressStatus');

                container.style.display = 'block';
                status.innerText = "Transcribing...";
                status.style.color = 'orange';
                progressBar.style.width = "0%";

                const interval = setInterval(() => {
                    if (progress < 95) {
                        progress += Math.random() * 4; // Simulated speed
                        progressBar.style.width = `${Math.min(progress, 95)}%`;
                    }
                }, 200);

                callback(() => {
                    clearInterval(interval);
                    progressBar.style.width = "100%";
                    status.innerText = "Transcribed ✅";
                    status.style.color = 'lightgreen';
                });
            }

            function transcribe() {
                if (!uploadedFileName) {
                    alert("Please upload a file first!");
                    return;
                }

                const resultBox = document.getElementById('transcriptionResult');
                resultBox.innerText = "";

                simulateProgressBar(done => {
                    fetch(`/transcribe/${uploadedFileName}`)
                        .then(response => response.json())
                        .then(data => {
                            resultBox.innerText = data.transcription;
                            resultBox.innerHTML += `<br><br><a href="${data.shareable_link}" target="_blank">Share Transcription</a>`;
                            done();
                        })
                        .catch(err => {
                            resultBox.innerText = "Error in transcription.";
                            document.getElementById("progressStatus").innerText = "Error ❌";
                            document.getElementById("progressStatus").style.color = "red";
                            console.error(err);
                        });
                });
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    cloudinary_response = await uu.save_and_upload(file)
    cloudinary_url = cloudinary_response.get("secure_url") if isinstance(cloudinary_response, dict) else None

    if not cloudinary_url:
        return {"error": "Upload failed", "detail": str(cloudinary_response)}

    return {
        "filename": cloudinary_response.get("public_id"),
        "url": cloudinary_url,
        "message": "File uploaded successfully"
    }

@app.get("/transcribe/{filename}")
async def transcribe_audio(filename: str):
    cloudinary_url = f"https://res.cloudinary.com/dunfulrqo/video/upload/{filename}.mp3"
    result = wu.transcribe_audio_from_url(cloudinary_url)
    
    # Generate the shareable link
    shareable_link = f"/transcription/{filename}"

    return {
        "transcription": result['text'],
        "shareable_link": shareable_link
    }

@app.get("/transcription/{filename}")
async def get_transcription(filename: str):
    # This is to fetch the transcription from the server
    # In a real implementation, you would fetch saved transcriptions from storage
    return {"transcription": "This is a mock transcription for " + filename}
