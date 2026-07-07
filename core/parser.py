import re
from typing import Optional


class TitleParser:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.title_patterns_to_remove = self.config.get('metadata', {}).get('title_patterns_to_remove', [
            r'\s*[\(\[][^\)\]]*Official\s*(Music\s*)?Video[^\)\]]*[\)\]]',
            r'\s*[\(\[][^\)\]]*Official\s*Audio[^\)\]]*[\)\]]',
            r'\s*[\(\[]Audio[\)\]]',
            r'\s*[\(\[]Video[\)\]]',
            r'\s*[\(\[]HD[\)\]]',
            r'\s*[\(\[]4K[\)\]]',
            r'\s*[\(\[]Lyrics[\)\]]',
            r'\s*[\(\[]Lyric[\)\]]',
        ])

    def parse_youtube_title(self, title: str, uploader: Optional[str] = None) -> dict:
        artist, song_title = self._split_artist_title(title)
        cleaned_title = self._clean_title(song_title)

        return {
            'artist': artist or uploader or self.config.get('metadata', {}).get('default_artist', 'Unknown Artist'),
            'title': cleaned_title,
        }

    def _split_artist_title(self, title: str) -> tuple:
        separators = [' - ', ' – ', ' — ', ' | ', ': ']
        for sep in separators:
            if sep in title:
                parts = title.split(sep, 1)
                return parts[0].strip(), parts[1].strip()

        feat_patterns = [
            r'^(.*?)\s*(?:feat\.|ft\.|featuring)\s*(.*?)$',
            r'^(.*?)\s*\((?:feat\.|ft\.|featuring)\s*(.*?)\)$',
        ]
        for pattern in feat_patterns:
            match = re.match(pattern, title, re.IGNORECASE)
            if match:
                return match.group(1).strip(), title

        return None, title

    def _clean_title(self, title: str) -> str:
        cleaned = title
        for pattern in self.title_patterns_to_remove:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'^[-–—\s]+|[-–—\s]+$', '', cleaned)

        return cleaned

    def parse_playlist_title(self, playlist_title: str) -> dict:
        artist, album = self._split_artist_title(playlist_title)

        return {
            'artist': artist or self.config.get('metadata', {}).get('default_artist', 'Unknown Artist'),
            'album': album or playlist_title or self.config.get('metadata', {}).get('default_album', 'Unknown Album'),
        }

    def parse_upload_date(self, upload_date: str) -> Optional[str]:
        if not upload_date or len(upload_date) != 8:
            return None

        year = upload_date[:4]
        month = upload_date[4:6]
        day = upload_date[6:8]

        return f"{year}-{month}-{day}"
