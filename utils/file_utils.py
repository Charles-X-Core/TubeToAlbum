import os
from typing import Optional


def ensure_directory(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_file_extension(filepath: str) -> str:
    _, ext = os.path.splitext(filepath)
    return ext.lstrip('.')


def get_file_size(filepath: str) -> int:
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def safe_filename(filename: str) -> str:
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    sanitized = sanitized.strip('. ')
    return sanitized


def file_exists(filepath: str) -> bool:
    return os.path.exists(filepath) and os.path.isfile(filepath)


def delete_file(filepath: str) -> bool:
    if file_exists(filepath):
        os.remove(filepath)
        return True
    return False
