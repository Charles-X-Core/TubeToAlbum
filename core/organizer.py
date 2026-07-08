import os
import re
from typing import Optional


class FileOrganizer:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.output_template = self.config.get('output_template',
            '%(artist|uploader)s/%(album|playlist)s/%(title)s.%(ext)s')
        self.output_dir = self.config.get('default_output_dir', os.path.expanduser('~/Music'))
        self.non_music_output_dir = self.config.get('non_music_output_dir',
            os.path.expanduser('~/Downloads/TubeToAlbum'))
        self.non_music_video_subdir = self.config.get('non_music_video_subdir', 'Videos')
        self.non_music_template = self.config.get('non_music_template',
            '%(uploader)s/%(title)s.%(ext)s')

    def sanitize_filename(self, name) -> str:
        if isinstance(name, list):
            name = name[0] if name else ''
        if not name:
            return ''
        name = str(name).split(',')[0].strip()
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        sanitized = sanitized.strip('. ')
        return sanitized

    def sanitize_artist(self, name) -> str:
        if isinstance(name, list):
            name = name[0] if name else ''
        if not name:
            return ''
        name = str(name)
        name = re.split(r'\s*[,]\s*', name)[0].strip()
        name = re.split(r'\s+(?:feat\.|ft\.|featuring)\s+', name, flags=re.IGNORECASE)[0].strip()
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        sanitized = sanitized.strip('. ')
        return sanitized

    def generate_music_filename(self, metadata: dict) -> str:
        template = self.output_template

        artist = self.sanitize_artist(metadata.get('artist', 'Unknown Artist'))
        album = self.sanitize_filename(metadata.get('album', 'Unknown Album'))
        title = self.sanitize_filename(metadata.get('title', 'Unknown Title'))
        ext = metadata.get('ext', 'mp3')
        year = metadata.get('year', '')

        filename = template
        filename = filename.replace('%(artist|uploader)s', artist)
        filename = filename.replace('%(album|playlist)s', album)
        filename = filename.replace('%(title)s', title)
        filename = filename.replace('%(ext)s', ext)
        filename = filename.replace('%(year)s', str(year))

        return filename

    def generate_video_filename(self, metadata: dict) -> str:
        template = self.non_music_template

        uploader = self.sanitize_filename(metadata.get('uploader', 'Unknown Uploader'))
        title = self.sanitize_filename(metadata.get('title', 'Unknown Title'))
        ext = metadata.get('ext', 'mp4')

        filename = template
        filename = filename.replace('%(uploader)s', uploader)
        filename = filename.replace('%(title)s', title)
        filename = filename.replace('%(ext)s', ext)

        return filename

    def get_music_path(self, metadata: dict) -> str:
        filename = self.generate_music_filename(metadata)
        return os.path.join(os.path.expanduser(self.output_dir), filename)

    def get_video_path(self, metadata: dict) -> str:
        filename = self.generate_video_filename(metadata)
        return os.path.join(
            os.path.expanduser(self.non_music_output_dir),
            self.non_music_video_subdir,
            filename
        )

    def create_directories(self, filepath: str):
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _handle_duplicate(self, dest_path: str) -> str:
        if os.path.exists(dest_path) and not self.config.get('overwrite_existing', False):
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(dest_path):
                dest_path = f"{base} ({counter}){ext}"
                counter += 1
        return dest_path

    def organize_music_file(self, source_path: str, metadata: dict) -> str:
        dest_path = self.get_music_path(metadata)
        dest_path = self._handle_duplicate(dest_path)
        self.create_directories(dest_path)

        if os.path.exists(source_path):
            os.rename(source_path, dest_path)

        return dest_path

    def organize_video_file(self, source_path: str, metadata: dict) -> str:
        dest_path = self.get_video_path(metadata)
        dest_path = self._handle_duplicate(dest_path)
        self.create_directories(dest_path)

        if os.path.exists(source_path):
            os.rename(source_path, dest_path)

        return dest_path

    def organize_file(self, source_path: str, metadata: dict, is_music: bool = True) -> str:
        if is_music:
            return self.organize_music_file(source_path, metadata)
        else:
            return self.organize_video_file(source_path, metadata)

    def get_existing_files(self) -> list:
        files = []
        for base_dir in [self.output_dir, self.non_music_output_dir]:
            expanded = os.path.expanduser(base_dir)
            if os.path.exists(expanded):
                for root, dirs, filenames in os.walk(expanded):
                    for filename in filenames:
                        if filename.lower().endswith(('.mp3', '.m4a', '.flac', '.mp4', '.webm')):
                            files.append(os.path.join(root, filename))
        return files

    def find_duplicates(self, metadata: dict, is_music: bool = True) -> list:
        if is_music:
            target_path = self.get_music_path(metadata)
        else:
            target_path = self.get_video_path(metadata)
        existing = self.get_existing_files()
        return [f for f in existing if f == target_path]
