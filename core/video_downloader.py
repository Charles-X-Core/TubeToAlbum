import yt_dlp
import os
from typing import Optional, Callable


class VideoDownloader:
    def __init__(self, config: dict):
        self.config = config
        self.ydl_opts = self._build_options()

    def _build_options(self) -> dict:
        output_dir = self.config.get('non_music_output_dir', '')
        video_subdir = self.config.get('non_music_video_subdir', 'Videos')
        output_template = self.config.get('output_template', '%(uploader)s/%(title)s.%(ext)s')

        if output_dir:
            outtmpl = os.path.join(os.path.expanduser(output_dir), video_subdir, output_template)
        else:
            outtmpl = os.path.join(os.path.expanduser('~/Downloads/TubeToAlbum'), video_subdir, output_template)

        return {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': outtmpl,
            'progress_hooks': [self._progress_hook],
            'quiet': self.config.get('quiet', False),
            'no_warnings': self.config.get('quiet', False),
            'restrictfilenames': True,
        }

    def get_info(self, url: str) -> Optional[dict]:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._parse_info(info)
        except Exception as e:
            raise Exception(f"Error extracting info: {e}")

    def download(self, url: str, progress_callback: Optional[Callable] = None) -> str:
        if progress_callback:
            self.ydl_opts['progress_hooks'] = [progress_callback]
        else:
            self.ydl_opts['progress_hooks'] = [self._progress_hook]

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])

    def _progress_hook(self, d: dict):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\r{percent} | Speed: {speed} | ETA: {eta}", end='')
        elif d['status'] == 'finished':
            print("\n¡Descarga completada!")

    def _parse_info(self, info: dict) -> dict:
        return {
            'title': info.get('title'),
            'artist': info.get('artist') or info.get('uploader'),
            'uploader': info.get('uploader'),
            'album': info.get('album') or info.get('playlist'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date'),
            'track_number': info.get('track_number') or info.get('playlist_index'),
            'description': info.get('description'),
            'categories': info.get('categories', []),
        }
