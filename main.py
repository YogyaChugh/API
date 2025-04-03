from flask import Flask, request, jsonify
import speech_recognition as sr
import pytesseract
from PIL import Image
import os

app = Flask(__name__)

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r"tesseract.exe"  # Change for Linux/macOS

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="auto")
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Speech recognition service unavailable."

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang="eng+hin")  # Supports multiple languages
    return text

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)
    
    if file.filename.endswith(".wav"):
        text = transcribe_audio(file_path)
    elif file.filename.endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image(file_path)
    else:
        return jsonify({"error": "Unsupported file format"}), 400
    
    os.remove(file_path)  # Cleanup
    return jsonify({"text": text})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
