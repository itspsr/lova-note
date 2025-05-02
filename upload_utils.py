import os
import tempfile
from fastapi import UploadFile
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
from typing import Optional, Dict

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

async def save_and_upload(file: UploadFile) -> Optional[Dict]:
    # Create a temp file to store the uploaded data
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        temp_filename = tmp.name

    try:
        response = cloudinary.uploader.upload(temp_filename, resource_type="auto")
        print("Cloudinary upload response:", response)
        return response
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")
        return None
    finally:
        # Clean up temp file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
