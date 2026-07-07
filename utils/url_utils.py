import re
from typing import Optional


def is_youtube_url(url: str) -> bool:
    patterns = [
        r'^(https?://)?(www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}',
        r'^(https?://)?(www\.)?music\.youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}',
        r'^(https?://)?(www\.)?youtu\.be/[a-zA-Z0-9_-]{11}',
        r'^(https?://)?(www\.)?youtube\.com/embed/[a-zA-Z0-9_-]{11}',
        r'^(https?://)?(www\.)?youtube\.com/v/[a-zA-Z0-9_-]{11}',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def is_youtube_playlist(url: str) -> bool:
    if 'start_radio=1' in url:
        return False
    patterns = [
        r'^(https?://)?(www\.)?youtube\.com/playlist\?list=[a-zA-Z0-9_-]+',
    ]
    return any(re.match(pattern, url) for pattern in patterns)


def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r'(?:v=|/v/|youtu\.be/|/embed/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def extract_playlist_id(url: str) -> Optional[str]:
    match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None


def clean_youtube_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url


def sanitize_youtube_url(url: str) -> str:
    """Remove list, start_radio and other unwanted params from YouTube URL."""
    import urllib.parse
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)

    video_id = None
    if 'v' in params:
        video_id = params['v'][0]

    if video_id:
        clean = f"https://www.youtube.com/watch?v={video_id}"
    elif 'youtu.be' in parsed.netloc:
        path = parsed.path.split('?')[0]
        clean = f"https://youtu.be{path}"
    elif 'music.youtube.com' in parsed.netloc:
        clean = f"https://www.youtube.com/watch?v={params['v'][0]}" if 'v' in params else url
    else:
        clean = url.split('&list=')[0].split('&start_radio=')[0]

    return clean
