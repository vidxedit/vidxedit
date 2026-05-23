from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import yt_dlp
import os
import requests as req

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

@app.route('/direct', methods=['GET'])
def direct_download():
    url = request.args.get('url')
    filename = request.args.get('filename', 'video.mp4')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        r = req.get(url, stream=True, timeout=30)
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': r.headers.get('Content-Type', 'video/mp4')
        }
        return Response(r.iter_content(chunk_size=8192), headers=headers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
