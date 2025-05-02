import shutil
import os
from fastapi import UploadFile
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary_config import cloudinary

async def save_and_upload(file: UploadFile):
    file_location = f"temp_{file.filename}"
    
    # Save temporarily to disk
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Upload to Cloudinary
    response = cloudinary_upload(file_location)
    
    # Remove local temp file
    os.remove(file_location)

    return response
