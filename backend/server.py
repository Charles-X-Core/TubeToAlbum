import sys
import os
import json
import uuid
import threading
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader import TubeToAlbumDownloader
from core.video_downloader import VideoDownloader
from core.content_detector import ContentDetector
from core.thumbnail import crop_to_square
from core.metadata import MetadataWriter
from utils.config_utils import load_config, save_config
from utils.url_utils import is_youtube_url, sanitize_youtube_url

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
HISTORY_PATH = os.path.join(BASE_DIR, 'history.json')

jobs = {}


def load_history():
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def _crop_and_reembed_thumbnail(audio_path: str, video_url: str = ''):
    try:
        thumb_data = None
        sidecar_path = None

        base = os.path.splitext(audio_path)[0]

        for ext in ['.jpg', '.webp', '.png', '.jpeg']:
            candidate = base + ext
            if os.path.exists(candidate):
                sidecar_path = candidate
                with open(candidate, 'rb') as f:
                    thumb_data = f.read()
                break

        if not thumb_data and video_url:
            from core.thumbnail import ThumbnailHandler
            handler = ThumbnailHandler()
            video_id = handler.get_video_id(video_url)
            if video_id:
                thumb_data = handler.download_best_thumbnail(video_id)

        if not thumb_data:
            return

        cropped = crop_to_square(thumb_data)

        if not os.path.exists(audio_path):
            return

        album_dir = os.path.dirname(audio_path)
        folder_jpg = os.path.join(album_dir, 'folder.jpg')
        with open(folder_jpg, 'wb') as f:
            f.write(cropped)

        from core.thumbnail import image_to_ico
        folder_ico = os.path.join(album_dir, 'folder.ico')
        ico_data = image_to_ico(cropped)
        with open(folder_ico, 'wb') as f:
            f.write(ico_data)

        desktop_ini = os.path.join(album_dir, 'desktop.ini')
        with open(desktop_ini, 'w', encoding='utf-16-le') as f:
            f.write('[.ShellClassInfo]\nIconResource=folder.ico,0\n')
        try:
            import ctypes
            ctypes.windll.kernel32.SetFileAttributesW(desktop_ini, 0x06)
            ctypes.windll.kernel32.SetFileAttributesW(album_dir, 0x01)
            import subprocess
            subprocess.run(['powershell', '-Command',
                          f'Unblock-File -Path "{desktop_ini}"'],
                         capture_output=True, timeout=5)
        except Exception:
            pass

        writer = MetadataWriter(audio_path)
        writer.write_thumbnail(cropped)
        writer.save()

        if sidecar_path and os.path.exists(sidecar_path):
            os.remove(sidecar_path)

    except Exception as e:
        import traceback
        print(f"[THUMB] ERROR: {traceback.format_exc()}", flush=True)


@app.route('/api/info', methods=['POST'])
def get_info():
    try:
        data = request.json
        url = data.get('url', '')
        if not url:
            return jsonify({'error': 'URL requerida'}), 400

        if not is_youtube_url(url):
            return jsonify({'error': 'URL de YouTube no valida'}), 400

        url = sanitize_youtube_url(url)
        config = load_config()
        downloader = TubeToAlbumDownloader({'quiet': True})
        info = downloader.get_info(url)
        if info is None:
            return jsonify({'error': 'No se pudo obtener la informacion'}), 404

        info['url'] = url
        detector = ContentDetector()
        analysis = detector.detect(info)

        return jsonify({'info': info, 'analysis': analysis})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def start_download():
    try:
        data = request.json
        url = data.get('url', '')
        fmt = data.get('format', 'mp3')
        quality = data.get('quality', '192')
        output_dir = data.get('output_dir', '')
        is_music = data.get('is_music', True)

        if not url:
            return jsonify({'error': 'URL requerida'}), 400

        url = sanitize_youtube_url(url)
        job_id = str(uuid.uuid4())[:8]

        jobs[job_id] = {
            'status': 'downloading',
            'progress': 0,
            'speed': '',
            'eta': '',
            'filepath': '',
            'error': '',
        }

        def progress_hook(d):
            if d['status'] == 'downloading':
                percent_str = d.get('_percent_str', '0%')
                import re
                clean = re.sub(r'\x1b\[[0-9;]*m', '', str(percent_str))
                clean = clean.replace('%', '').strip()
                try:
                    jobs[job_id]['progress'] = float(clean)
                except (ValueError, AttributeError):
                    jobs[job_id]['progress'] = 0

                speed = d.get('_speed_str', 'N/A')
                jobs[job_id]['speed'] = re.sub(r'\x1b\[[0-9;]*m', '', str(speed)).strip()

                eta = d.get('_eta_str', 'N/A')
                jobs[job_id]['eta'] = re.sub(r'\x1b\[[0-9;]*m', '', str(eta)).strip()

            elif d['status'] == 'finished':
                jobs[job_id]['progress'] = 100
                jobs[job_id]['status'] = 'completed'

        def run_download():
            try:
                if fmt == 'mp4':
                    vid_config = {
                        'non_music_output_dir': output_dir or os.path.expanduser('~/Downloads/TubeToAlbum'),
                        'non_music_video_subdir': '',
                        'video_quality': quality,
                        'quiet': True,
                    }
                    vid_downloader = VideoDownloader(vid_config)
                    filepath = vid_downloader.download(url, progress_callback=progress_hook)
                else:
                    expanded_dir = os.path.expandvars(output_dir) if output_dir else ''
                    dl_config = {
                        'format': fmt,
                        'quality': quality,
                        'quiet': True,
                        'non_music_output_dir': expanded_dir or os.path.expanduser('~/Downloads/TubeToAlbum'),
                        'default_output_dir': expanded_dir or os.path.expanduser('~/Music'),
                        'output_template': '%(artist|uploader)s/%(album|playlist)s/%(title)s.%(ext)s',
                    }
                    downloader = TubeToAlbumDownloader(dl_config)
                    filepath = downloader.download(url, progress_callback=progress_hook, is_music=is_music)

                if filepath:
                    filepath = os.path.normpath(filepath)

                jobs[job_id]['filepath'] = filepath or ''
                jobs[job_id]['status'] = 'completed'
                jobs[job_id]['progress'] = 100

                info_downloader = TubeToAlbumDownloader({'quiet': True})
                info = info_downloader.get_info(url)

                if filepath and fmt != 'mp4' and os.path.exists(filepath):
                    _crop_and_reembed_thumbnail(filepath, url)

                file_size = 0
                if filepath and os.path.exists(filepath):
                    try:
                        file_size = os.path.getsize(filepath)
                    except OSError:
                        file_size = 0

                entry = {
                    'title': info.get('title', 'Sin titulo') if info else 'Sin titulo',
                    'artist': info.get('artist', 'Desconocido') if info else 'Desconocido',
                    'format': fmt.upper(),
                    'filepath': filepath or '',
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'size': file_size,
                    'url': url,
                }

                for key in ['title', 'artist']:
                    if entry[key]:
                        entry[key] = entry[key].encode('utf-8', errors='replace').decode('utf-8', errors='replace')

                history = load_history()
                history.insert(0, entry)
                if len(history) > 100:
                    history = history[:100]
                save_history(history)

            except Exception as e:
                import traceback
                print(f"[ERROR] Download failed: {traceback.format_exc()}", flush=True)
                jobs[job_id]['status'] = 'error'
                jobs[job_id]['error'] = str(e)

        thread = threading.Thread(target=run_download, daemon=True)
        thread.start()

        return jsonify({'job_id': job_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress/<job_id>')
def get_progress(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job no encontrado'}), 404
    return jsonify(jobs[job_id])


@app.route('/api/cancel/<job_id>', methods=['POST'])
def cancel_download(job_id):
    if job_id not in jobs:
        return jsonify({'error': 'Job no encontrado'}), 404
    jobs[job_id]['status'] = 'cancelled'
    return jsonify({'ok': True})


@app.route('/api/history')
def get_history():
    return jsonify(load_history())


@app.route('/api/history', methods=['DELETE'])
def clear_history():
    save_history([])
    return jsonify({'ok': True})


@app.route('/api/history/<int:index>', methods=['DELETE'])
def delete_history_entry(index):
    history = load_history()
    if 0 <= index < len(history):
        history.pop(index)
        save_history(history)
        return jsonify({'ok': True})
    return jsonify({'error': 'Indice invalido'}), 400


@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify(load_config())


@app.route('/api/config', methods=['POST'])
def save_config_endpoint():
    try:
        config = request.json
        save_config(config, CONFIG_PATH)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("TubeToAlbum Backend API")
    print("http://localhost:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)
