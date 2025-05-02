from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import uuid
import logging
from whisper_utils import transcribe_audio, export_to_pdf, export_to_docx

app = Flask(__name__)

# Enable logging to track requests
logging.basicConfig(level=logging.DEBUG)

UPLOAD_FOLDER = 'uploads'
TRANSCRIPT_FOLDER = 'transcriptions'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def log_request():
    app.logger.debug(f"Incoming request: {request.path}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file uploaded!"}), 400

    file = request.files['audio']
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only audio files are allowed."}), 400

    lang = request.form.get('lang') or 'auto'
    model_size = request.form.get('model_size') or 'large-v3'
    feedback = request.form.get('feedback', "")

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        result = transcribe_audio(filepath, model_size, lang)

        if feedback:
            with open("feedback_logs.txt", "a") as f:
                f.write(f"{result['timestamp']}: {feedback}\n\n")

        audio_path = f"/uploads/{filename}"  # public path for playback

        return jsonify({**result, "audioPath": audio_path, "audioFilename": filename})

    except Exception as e:
        app.logger.error(f"Error during transcription: {str(e)}")
        return jsonify({"error": f"An error occurred during transcription: {str(e)}"}), 500

    # Don't delete the file here since it's needed for playback/download
    # Consider cleanup strategy or cron job

@app.route('/export/<format>/<filename>')
def export(format, filename):
    text = request.args.get('text')
    metadata = {
        "language": request.args.get('language'),
        "confidence": float(request.args.get('confidence', 0)),
        "duration": float(request.args.get('duration', 0)),
        "timestamp": request.args.get('timestamp'),
        "audio_path": request.args.get('audio_path', "N/A")
    }

    if not text or not metadata.get("language"):
        return jsonify({"error": "Missing required data for export!"}), 400

    try:
        if format == 'pdf':
            path = export_to_pdf(text, metadata, os.path.join(TRANSCRIPT_FOLDER, filename))
        elif format == 'docx':
            path = export_to_docx(text, metadata, os.path.join(TRANSCRIPT_FOLDER, filename))
        else:
            return jsonify({"error": "Unsupported format!"}), 400
    except Exception as e:
        app.logger.error(f"Error during export: {str(e)}")
        return jsonify({"error": f"Error during export: {str(e)}"}), 500

    return send_from_directory(TRANSCRIPT_FOLDER, filename, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.errorhandler(404)
def page_not_found(error):
    app.logger.warning(f"Undefined route accessed: {request.path}")
    return jsonify({"error": "This route does not exist!"}), 404

if __name__ == '__main__':
    app.run(debug=True)
