from flask import Flask, request, render_template, jsonify
from googletrans import Translator
import asyncio
import edge_tts
import os

app = Flask(__name__)
translator = Translator()

# 翻訳処理
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get("text")
    target_lang = data.get("target_lang", "en")  # デフォルトは英語

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # 翻訳
    translated = translator.translate(text, dest=target_lang)
    translated_text = translated.text

    return jsonify({"translated_text": translated_text})


# 音声合成処理
@app.route("/speak", methods=["POST"])
def speak():
    data = request.get_json()
    text = data.get("text")
    lang = data.get("lang", "en")  # デフォルト英語

    if not text:
        return jsonify({"error": "No text to speak"}), 400

    # Edge TTS の音声設定（lang に応じて自動選択）
    voice_map = {
        "en": "en-US-AriaNeural",
        "ja": "ja-JP-NanamiNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "it": "it-IT-ElsaNeural",
        "es": "es-ES-ElviraNeural",
        "zh-cn": "zh-CN-XiaoxiaoNeural",
        "ko": "ko-KR-SunHiNeural",
        "vi": "vi-VN-HoaiMyNeural"
    }

    voice = voice_map.get(lang, "en-US-AriaNeural")
    output_file = "static/output.mp3"

    async def _speak():
        communicate = edge_tts.Communicate(text, voice=voice)
        await communicate.save(output_file)

    asyncio.run(_speak())

    return jsonify({"audio_url": "/" + output_file})


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
