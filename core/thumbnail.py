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
    if img.mode != 'RGB':
        img = img.convert('RGB')
    w, h = img.size

    if w == h:
        cropped = img
    else:
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        right = left + side
        bottom = top + side
        cropped = img.crop((left, top, right, bottom))

    output = io.BytesIO()
    cropped.save(output, format='JPEG', quality=95)
    return output.getvalue()


def prepare_cover(image_data: bytes, target_size: int = 1024) -> bytes:
    img = Image.open(io.BytesIO(image_data))
    if img.mode != 'RGB':
        img = img.convert('RGB')

    if img.size[0] != target_size or img.size[1] != target_size:
        img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    from PIL import ImageFilter
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=100, threshold=3))

    output = io.BytesIO()
    img.save(output, format='JPEG', quality=95)
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
    import struct
    img = Image.open(io.BytesIO(image_data))
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256), (512, 512)]
    num = len(sizes)
    header = struct.pack('<HHH', 0, 1, num)
    data_offset = 6 + (num * 16)
    chunks = []
    entries = b''
    for size in sizes:
        resized = img.resize(size, Image.Resampling.LANCZOS)
        w = resized.width if resized.width < 256 else 0
        h = resized.height if resized.height < 256 else 0
        buf = io.BytesIO()
        resized.save(buf, format='PNG', optimize=False)
        png = buf.getvalue()
        chunks.append(png)
        entries += struct.pack('<BBBBHHII', w, h, 0, 0, 1, 32, len(png), data_offset)
        data_offset += len(png)
    return header + entries + b''.join(chunks)
