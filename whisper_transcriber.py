import whisper
import os
import torchaudio
import librosa

model = whisper.load_model("medium")

def transcribe_audio(audio_path):
    audio = whisper.load_audio(audio_path)
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    _, probs = model.detect_language(mel)
    detected_lang = max(probs, key=probs.get)

    result = model.transcribe(audio_path, language=detected_lang)
    duration = librosa.get_duration(path=audio_path)
    return {
        "text": result["text"],
        "duration": round(duration, 2),
        "language": detected_lang
    }
