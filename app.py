from flask import Flask, request, jsonify, render_template
import edge_tts
from googletrans import Translator
import uuid
import asyncio
import os

app = Flask(__name__)

# フォルダ作成
os.makedirs("static", exist_ok=True)

# 翻訳用
translator = Translator()

# 言語コード → edge-tts の voice 名マッピング
VOICE_MAP = {
    "ja": "ja-JP-NanamiNeural",
    "en": "en-US-AriaNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "zh-cn": "zh-CN-XiaoxiaoNeural",
    "zh-tw": "zh-TW-YatingNeural",
    "es": "es-ES-ElviraNeural",
    "ko": "ko-KR-SunHiNeural"
}

# 非同期で音声生成
async def text_to_speech(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/translate_tts", methods=["POST"])
def translate_tts():
    try:
        text_input = request.form.get("text", "")
        target_lang = request.form.get("target_lang", "ja")

        if not text_input.strip():
            text_input = "(入力なし)"

        # 翻訳
        translated = translator.translate(text_input, dest=target_lang)
        translated_text = translated.text

        # voice 選択
        voice_name = VOICE_MAP.get(target_lang, "en-US-AriaNeural")

        # tts 保存ファイル
        tts_filename = f"{uuid.uuid4()}.mp3"
        tts_path = os.path.join("static", tts_filename)

        # 非同期実行
        asyncio.run(text_to_speech(translated_text, voice_name, tts_path))

        return jsonify({
            "translated_text": translated_text,
            "audio_file": "/" + tts_path.replace("\\", "/")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
