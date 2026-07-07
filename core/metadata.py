from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TRCK, TDRC, TCON, APIC, ID3NoHeaderError
from typing import Optional
import subprocess


class MetadataWriter:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.audio = MP3(filepath, ID3=ID3)

        if self.audio.tags is None:
            self.audio.add_tags()

    def write_basic(self, title: str, artist: str, album: str):
        self.audio.tags.add(TIT2(encoding=3, text=title))
        self.audio.tags.add(TPE1(encoding=3, text=artist))
        self.audio.tags.add(TALB(encoding=3, text=album))

    def write_extended(self, track_number: Optional[int] = None, year: Optional[str] = None, genre: Optional[str] = None):
        if track_number:
            self.audio.tags.add(TRCK(encoding=3, text=str(track_number)))
        if year:
            self.audio.tags.add(TDRC(encoding=3, text=str(year)))
        if genre:
            self.audio.tags.add(TCON(encoding=3, text=genre))

    def write_thumbnail(self, thumbnail_data: bytes):
        self.audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc='Cover',
            data=thumbnail_data
        ))

    def write_all(self, metadata: dict):
        self.write_basic(
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album']
        )

        self.write_extended(
            track_number=metadata.get('track_number'),
            year=metadata.get('year'),
            genre=metadata.get('genre')
        )

        if metadata.get('thumbnail_data'):
            self.write_thumbnail(metadata['thumbnail_data'])

    def save(self):
        self.audio.save()

    def read(self) -> dict:
        return {
            'title': str(self.audio.tags.get('TIT2', '')),
            'artist': str(self.audio.tags.get('TPE1', '')),
            'album': str(self.audio.tags.get('TALB', '')),
            'track_number': str(self.audio.tags.get('TRCK', '')),
            'year': str(self.audio.tags.get('TDRC', '')),
            'genre': str(self.audio.tags.get('TCON', '')),
        }

    @staticmethod
    def create_test_mp3(filepath: str, duration: float = 0.1):
        subprocess.run([
            'ffmpeg', '-y', '-f', 'lavfi', '-i', f'sine=frequency=440:duration={duration}',
            '-codec:a', 'libmp3lame', '-b:a', '128k', filepath
        ], capture_output=True, check=True)
