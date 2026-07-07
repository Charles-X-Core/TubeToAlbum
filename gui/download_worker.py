import sys
import os
import re
from PySide6.QtCore import QThread, Signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader import TubeToAlbumDownloader
from core.video_downloader import VideoDownloader
from core.content_detector import ContentDetector
from utils.url_utils import sanitize_youtube_url


def clean_percent(raw):
    """Clean yt-dlp percent string (remove ANSI codes, whitespace, %)."""
    if not raw:
        return 0.0
    clean = re.sub(r'\x1b\[[0-9;]*m', '', str(raw))
    clean = clean.replace('%', '').strip()
    try:
        return float(clean)
    except (ValueError, AttributeError):
        return 0.0


def clean_speed(raw):
    """Clean yt-dlp speed string."""
    if not raw:
        return 'N/A'
    return re.sub(r'\x1b\[[0-9;]*m', '', str(raw)).strip()


class InfoWorker(QThread):
    finished = Signal(dict, dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = sanitize_youtube_url(url)

    def run(self):
        try:
            config = {'quiet': True}
            downloader = TubeToAlbumDownloader(config)
            info = downloader.get_info(self.url)
            if info is None:
                self.error.emit("No se pudo obtener la informacion del video.")
                return

            info['url'] = self.url
            detector = ContentDetector()
            analysis = detector.detect(info)
            self.finished.emit(info, analysis)
        except Exception as e:
            self.error.emit(str(e))


class DownloadWorker(QThread):
    progress_updated = Signal(float, str, str)
    download_finished = Signal(str)
    download_error = Signal(str)

    def __init__(self, url, fmt, quality, output_dir, is_music, config):
        super().__init__()
        self.url = sanitize_youtube_url(url)
        self.fmt = fmt
        self.quality = quality
        self.output_dir = output_dir
        self.is_music = is_music
        self.config = config
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            def progress_hook(d):
                if self._cancelled:
                    raise Exception("Descarga cancelada por el usuario")
                if d['status'] == 'downloading':
                    percent = clean_percent(d.get('_percent_str', '0%'))
                    speed = clean_speed(d.get('_speed_str', 'N/A'))
                    eta = clean_speed(d.get('_eta_str', 'N/A'))
                    self.progress_updated.emit(percent, speed, eta)
                elif d['status'] == 'finished':
                    self.progress_updated.emit(100.0, 'Completado', '0s')

            if self.fmt == 'mp4':
                vid_config = {
                    'non_music_output_dir': self.output_dir,
                    'non_music_video_subdir': '',
                    'video_quality': self.quality,
                    'quiet': True,
                }
                vid_downloader = VideoDownloader(vid_config)
                filepath = vid_downloader.download(self.url, progress_callback=progress_hook)
                self.download_finished.emit(filepath or self.output_dir)
            else:
                dl_config = {
                    'format': self.fmt if self.fmt != 'm4a' else 'm4a',
                    'quality': self.quality,
                    'quiet': True,
                    'non_music_output_dir': self.output_dir,
                }
                downloader = TubeToAlbumDownloader(dl_config)
                filepath = downloader.download(self.url, progress_callback=progress_hook, is_music=self.is_music)
                self.download_finished.emit(filepath or self.output_dir)

        except Exception as e:
            if "cancelada" in str(e).lower():
                self.download_error.emit("Descarga cancelada")
            else:
                self.download_error.emit(str(e))
