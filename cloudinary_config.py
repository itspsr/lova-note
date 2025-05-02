import os
from dotenv import load_dotenv
import cloudinary

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("dunfulrqo"),
    api_key=os.getenv("419193645861974"),
    api_secret=os.getenv("6GQKnTWDXGnoelDYCp3kR6rZzJ0")
)
