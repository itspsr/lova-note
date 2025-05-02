import os
import whisper
import librosa
import torch
import soundfile as sf
import torchaudio
import requests
import re
from datetime import datetime
from fpdf import FPDF
from docx import Document
import openai
from dotenv import load_dotenv

# === Constants ===
UPLOAD_FOLDER = 'uploads'
TRANSCRIPT_FOLDER = 'transcriptions'

# === Load environment variables ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "te": "Telugu", "ta": "Tamil",
    "gu": "Gujarati", "ml": "Malayalam", "kn": "Kannada", "mr": "Marathi", "pa": "Punjabi", "ur": "Urdu"
}

def get_language_name(code):
    return LANGUAGE_NAMES.get(code, code)

def get_audio_duration(filepath):
    audio, sr = librosa.load(filepath, sr=None)
    return librosa.get_duration(y=audio, sr=sr)

def detect_language(filepath, model_size='base'):
    model = whisper.load_model(model_size)
    audio = whisper.load_audio(filepath)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    _, probs = model.detect_language(mel)
    lang_probs = {k: float(v) for k, v in probs.items()}
    detected_lang = max(lang_probs, key=lang_probs.get)
    confidence = lang_probs[detected_lang]

    if detected_lang not in LANGUAGE_NAMES:
        print(f"[Warning] Detected unknown language '{detected_lang}', defaulting to English.")
        detected_lang = "en"

    return str(detected_lang), confidence

def download_audio_from_cloudinary(url):
    response = requests.get(url)
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    file_path = os.path.join(UPLOAD_FOLDER, 'temp_audio.mp3')

    with open(file_path, 'wb') as f:
        f.write(response.content)

    return file_path

def preprocess_audio(filepath):
    waveform, sample_rate = torchaudio.load(filepath)
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
    waveform = waveform / waveform.abs().max()
    base, _ = os.path.splitext(filepath)
    temp_path = f"{base}_preprocessed.wav"
    sf.write(temp_path, waveform.squeeze(0).numpy(), 16000)
    return temp_path

def clean_transcription(text):
    cleaned_text = re.sub(r'\b(um|uh|ah|like|you know)\b', '', text)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that cleans and improves transcription text."},
                {"role": "user", "content": f"Clean and perfect the following transcription text for grammar, punctuation, and readability:\n{text}"}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        cleaned_text = response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"[GPT CLEANING ERROR] {e}")
        cleaned_text = text
    return cleaned_text

def transcribe_audio_from_url(audio_url: str, model_size='base', lang='auto') -> dict:
    """
    Transcribes audio from a given URL using Whisper.
    Returns the transcription, language, confidence, and other metadata.
    """
    # Step 1: Download the audio from the URL
    file_path = download_audio_from_cloudinary(audio_url)
    
    # Step 2: Preprocess the audio
    preprocessed_path = preprocess_audio(file_path)
    
    # Step 3: Detect language if 'auto' is specified
    model = whisper.load_model(model_size)
    
    if lang == 'auto':
        lang, confidence = detect_language(preprocessed_path, model_size)
    else:
        confidence = None

    # Step 4: Perform transcription
    result = model.transcribe(preprocessed_path, language=lang)
    cleaned_text = clean_transcription(result['text'])

    return {
        'text': cleaned_text,
        'language': lang,
        'confidence': confidence,
        'accuracy_rate': (confidence * 100) if confidence is not None else 100.0,
        'duration': get_audio_duration(preprocessed_path),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'audio_path': file_path
    }
