from flask import Flask, request, jsonify
from pytube import YouTube
import whisper
import os
from moviepy.editor import AudioFileClip

app = Flask(__name__)

TEMP_DIR = "temp_audio"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.route('/extract-script', methods=['POST'])
def extract_script():
    try:
        data = request.get_json()
        video_url = data.get("url")

        if not video_url:
            return jsonify({"error": "No URL provided"}), 400

        yt = YouTube(video_url)
        video_stream = yt.streams.filter(only_audio=True).first()
        audio_file_path = f"{TEMP_DIR}/{yt.title}.mp4"
        video_stream.download(output_path=TEMP_DIR, filename=yt.title)

        audio_clip = AudioFileClip(audio_file_path)
        audio_path = f"{TEMP_DIR}/{yt.title}.wav"
        audio_clip.write_audiofile(audio_path)
        audio_clip.close()

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)

        os.remove(audio_file_path)
        os.remove(audio_path)

        return jsonify({"script": result["text"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
