from flask import Flask, request, jsonify, render_template
from gtts import gTTS
from googletrans import Translator
import os
import uuid
import glob

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

translator = Translator()

import sounddevice as sd
import pygame

try:
    print("Sounddevice default device:", sd.query_devices())
except Exception as e:
    print("Sounddevice error:", e)

try:
    pygame.mixer.init()
    print("Pygame audio initialized")
except Exception as e:
    print("Pygame error:", e)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/translate_tts", methods=["POST"])
def translate_tts():
    # Whisper は使用せず、テキスト入力のみ対応
    recognized_text = request.form.get("text", "").strip()
    target_lang = request.form.get("target_lang", "ja")

    if not recognized_text:
        return jsonify({"error": "No text input"}), 400

    # 翻訳
    translated = translator.translate(recognized_text, dest=target_lang)
    translated_text = translated.text

    # gTTS で音声生成
    tts_filename = f"{uuid.uuid4()}.mp3"
    tts_path = os.path.join("static", tts_filename)
    tts = gTTS(translated_text, lang=target_lang)
    tts.save(tts_path)

    # 古い mp3 を整理（最新 5 つだけ残す）
    mp3_files = sorted(glob.glob("static/*.mp3"), key=os.path.getmtime, reverse=True)
    for old_file in mp3_files[5:]:
        try:
            os.remove(old_file)
        except PermissionError:
            pass

    return jsonify({
        "recognized_text": recognized_text,
        "translated_text": translated_text,
         "audio_file": request.host_url.rstrip("/") + "/" + tts_path.replace("\\", "/")
    })

# 予期しない例外も JSON で返す
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
