from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'VidXEdit API is running!'

@app.route('/download', methods=['GET'])
def download():
    url = request.args.get('url')
    quality = request.args.get('quality', '720')
    audio_only = request.args.get('audio', 'false') == 'true'

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best' if audio_only else f'bestvideo[height<={quality}]+bestaudio/best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []

            if audio_only:
                formats.append({
                    'quality': 'MP3',
                    'url': info.get('url', ''),
                    'ext': 'mp3'
                })
            else:
                for f in info.get('formats', []):
                    if f.get('height') and f.get('url'):
                        formats.append({
                            'quality': f'{f["height"]}p',
                            'url': f['url'],
                            'ext': f.get('ext', 'mp4')
                        })

            return jsonify({
                'title': info.get('title', ''),
                'thumbnail': info.get('thumbnail', ''),
                'formats': formats
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
