import re
import requests
from typing import Optional
from PIL import Image
import io


class ThumbnailHandler:
    YOUTUBE_THUMBNAIL_URLS = {
        'maxresdefault': 'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
        'sddefault': 'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
        'hqdefault': 'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
        'mqdefault': 'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
        'default': 'https://img.youtube.com/vi/{video_id}/default.jpg',
    }

    def __init__(self):
        self.session = requests.Session()

    def get_video_id(self, url: str) -> Optional[str]:
        patterns = [
            r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def download_thumbnail(self, video_id: str, quality: str = 'maxresdefault') -> Optional[bytes]:
        url = self.YOUTUBE_THUMBNAIL_URLS.get(quality)
        if not url:
            return None

        url = url.format(video_id=video_id)

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception:
            pass

        return None

    def download_best_thumbnail(self, video_id: str) -> Optional[bytes]:
        qualities = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault']

        for quality in qualities:
            data = self.download_thumbnail(video_id, quality)
            if data:
                return data

        return None

    def resize_image(self, image_data: bytes, max_size: tuple = (500, 500)) -> bytes:
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()

    def save_thumbnail(self, image_data: bytes, filepath: str):
        with open(filepath, 'wb') as f:
            f.write(image_data)


def crop_to_square(image_data: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_data))
    w, h = img.size

    if w == h:
        return image_data

    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    right = left + side
    bottom = top + side

    cropped = img.crop((left, top, right, bottom))

    output = io.BytesIO()
    cropped.save(output, format='JPEG', quality=95)
    return output.getvalue()


def crop_thumbnail_file(filepath: str) -> bool:
    try:
        with open(filepath, 'rb') as f:
            data = f.read()

        cropped = crop_to_square(data)

        if cropped != data:
            with open(filepath, 'wb') as f:
                f.write(cropped)
            return True
        return False
    except Exception:
        return False


def image_to_ico(image_data: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_data))
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
    output = io.BytesIO()
    img.save(output, format='ICO', sizes=sizes)
    return output.getvalue()
