import whisper
import sys
import os

# Initialize the Whisper model
model = whisper.load_model("base")

# Get file path from command line arguments
audio_file_path = sys.argv[1]

# Check if file exists
if not os.path.exists(audio_file_path):
    print(f"❌ File does not exist: {audio_file_path}")
    sys.exit(1)

# Transcribe the audio file
try:
    print(f"🎧 Transcribing audio file: {audio_file_path}")
    
    # No progress_callback
    result = model.transcribe(audio_file_path)

    print(f"✅ Transcription completed successfully:\n{result['text']}")
except Exception as e:
    print(f"❌ Error during transcription: {str(e)}")
    sys.exit(1)
