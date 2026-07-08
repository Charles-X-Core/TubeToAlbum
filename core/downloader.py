import yt_dlp
import os
import re
from typing import Optional, Callable


class TubeToAlbumDownloader:
    def __init__(self, config: dict):
        self.config = config
        self.ydl_opts = self._build_options()

    def _build_options(self) -> dict:
        return {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.config.get('format', 'mp3'),
                    'preferredquality': self.config.get('quality', '192'),
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
            ],
            'writethumbnail': True,
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook],
            'quiet': self.config.get('quiet', False),
            'no_warnings': self.config.get('quiet', False),
            'restrictfilenames': True,
        }

    def _sanitize(self, name) -> str:
        if isinstance(name, list):
            name = name[0] if name else ''
        if not name:
            return ''
        name = str(name).split(',')[0].strip()
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        sanitized = sanitized.strip('. ')
        return sanitized

    def _build_output_path(self, info: dict, is_music: bool = True) -> str:
        if is_music:
            output_dir = self.config.get('output', {}).get('output_dir') or self.config.get('default_output_dir', '')
            output_template = self.config.get('output', {}).get('output_template') or self.config.get('output_template', '%(artist|uploader)s/%(album|playlist)s/%(title)s.%(ext)s')
        else:
            output_dir = self.config.get('non_music_output_dir', '~/Downloads/TubeToAlbum')
            output_template = '%(title)s.%(ext)s'

        artist = self._sanitize(info.get('artist') or info.get('uploader', 'Unknown Artist'))
        album = self._sanitize(info.get('album') or info.get('playlist', 'Unknown Album'))
        title = self._sanitize(info.get('title', 'Unknown Title'))
        ext = self.config.get('format', 'mp3')

        filename = output_template
        filename = filename.replace('%(artist|uploader)s', artist)
        filename = filename.replace('%(album|playlist)s', album)
        filename = filename.replace('%(title)s', title)
        filename = filename.replace('%(ext)s', '%(ext)s')

        if output_dir:
            expanded = os.path.expanduser(os.path.expandvars(output_dir))
            return os.path.normpath(os.path.join(expanded, filename))
        return filename

    def get_info(self, url: str) -> Optional[dict]:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return self._parse_info(info)
        except Exception as e:
            raise Exception(f"Error extracting info: {e}")

    def download(self, url: str, progress_callback: Optional[Callable] = None, is_music: bool = True) -> str:
        if progress_callback:
            self.ydl_opts['progress_hooks'] = [progress_callback]
        else:
            self.ydl_opts['progress_hooks'] = [self._progress_hook]

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            output_path = self._build_output_path(info, is_music)

            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            self.ydl_opts['outtmpl'] = output_path

            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl2:
                ydl2.download([url])

        final_ext = self.config.get('format', 'mp3')
        real_path = output_path.replace('%(ext)s', final_ext)
        if not os.path.exists(real_path):
            orig_ext = info.get('ext', 'webm')
            real_path = output_path.replace('%(ext)s', orig_ext)
        return real_path

    def download_playlist(self, playlist_url: str, progress_callback: Optional[Callable] = None) -> list:
        if progress_callback:
            self.ydl_opts['progress_hooks'] = [progress_callback]
        else:
            self.ydl_opts['progress_hooks'] = [self._progress_hook]

        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([playlist_url])

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
