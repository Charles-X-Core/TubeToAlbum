import json
import os
from typing import Optional


DEFAULT_CONFIG = {
    'default_quality': '192',
    'default_format': 'mp3',
    'output_template': '%(artist|uploader)s/%(album|playlist)s/%(title)s.%(ext)s',
    'default_output_dir': '~/Music',
    'non_music_output_dir': '~/Downloads/TubeToAlbum',
    'non_music_video_subdir': 'Videos',
    'non_music_template': '%(uploader)s/%(title)s.%(ext)s',
    'video_quality': 'best',
    'ask_format_for_non_music': True,
    'embed_metadata': True,
    'embed_thumbnail': True,
    'overwrite_existing': False,
    'metadata': {
        'clean_title': True,
        'default_genre': 'Music',
        'default_album': 'Unknown Album',
        'default_artist': 'Unknown Artist',
        'title_patterns_to_remove': [
            r'\(?Official(Music)?Video\)?',
            r'\[?Official(Music)?Video\]?',
            r'\(?Official Audio\)?',
            r'\(?Audio\)?',
            r'\(?Video\)?',
            r'\[?HD\]?',
            r'\[?4K\]?',
            r'\[?Lyrics\]?',
            r'\(?Lyrics\)?',
        ]
    },
    'download': {
        'max_concurrent': 3,
        'retry_count': 3,
        'retry_delay': 5,
        'timeout': 30
    }
}


def load_config(config_path: Optional[str] = None) -> dict:
    config = DEFAULT_CONFIG.copy()

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            config = merge_configs(config, user_config)
        except (json.JSONDecodeError, IOError):
            pass

    return config


def save_config(config: dict, config_path: str):
    directory = os.path.dirname(config_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def merge_configs(base: dict, override: dict) -> dict:
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def get_config_value(config: dict, key_path: str, default=None):
    keys = key_path.split('.')
    value = config

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
