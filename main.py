import io
import pytesseract
import speech_recognition as sr
from flask import Flask, request, jsonify
from PIL import Image

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Process WAV files (Audio-to-Text)
    if file.filename.endswith(".wav"):
        recognizer = sr.Recognizer()
        with sr.AudioFile(io.BytesIO(file.read())) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                text = "Could not understand audio"
            except sr.RequestError:
                text = "Speech recognition service unavailable"

    # Process Image files (OCR)
    elif file.filename.endswith((".png", ".jpg", ".jpeg")):
        image = Image.open(io.BytesIO(file.read()))
        text = pytesseract.image_to_string(image)

    else:
        return jsonify({"error": "Unsupported file format"}), 400

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(port=10000, debug=False)
