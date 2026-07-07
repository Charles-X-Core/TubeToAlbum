from typing import Optional
import re


class ContentDetector:
    MUSIC_TITLE_PATTERNS = [
        r'official\s*(music)?\s*video',
        r'official\s*audio',
        r'lyric[s]?',
        r'music\s*video',
        r'audio\s*only',
        r'cover\s*(version|by)?',
        r'acoustic',
        r'unplugged',
        r'live\s*(performance|session)',
        r'(song|track)',
        r'(remix|edit|mix)',
        r'(feat\.|ft\.)',
    ]

    NON_MUSIC_TITLE_PATTERNS = [
        r'tutorial',
        r'how\s*to',
        r'vlog',
        r'podcast',
        r'interview',
        r'review',
        r'gameplay',
        r'lets\s*play',
        r'news',
        r'sports',
        r'comedy\s*sketch',
        r'prank',
        r'documentary',
        r'lecture',
        r'talk',
        r'speech',
    ]

    MUSIC_CATEGORIES = [
        'music',
        'entertainment',
    ]

    def detect(self, video_info: dict) -> dict:
        score = 0
        reasons = []

        has_artist = bool(video_info.get('artist'))
        has_album = bool(video_info.get('album'))

        if has_artist and has_album:
            score += 3
            reasons.append(f'Tiene artista: {video_info["artist"]}')
            score += 3
            reasons.append(f'Tiene álbum: {video_info["album"]}')
        elif has_artist:
            score += 1
            reasons.append(f'Artista detectado (uploader): {video_info["artist"]}')
        elif video_info.get('uploader'):
            score += 0
            reasons.append(f'Canal: {video_info["uploader"]}')

        if video_info.get('track_number'):
            score += 2
            reasons.append('Tiene número de pista')

        if video_info.get('playlist'):
            score += 3
            reasons.append(f'Está en playlist: {video_info["playlist"]}')

        title = (video_info.get('title') or '').lower()

        for pattern in self.MUSIC_TITLE_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                score += 4
                reasons.append(f'Título contiene patrón musical')
                if video_info.get('uploader'):
                    score += 1
                break

        for pattern in self.NON_MUSIC_TITLE_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                score -= 4
                reasons.append(f'Título contiene patrón de no-música')
                break

        duration = video_info.get('duration', 0)
        if duration and 120 <= duration <= 420:
            score += 1
            reasons.append(f'Duración típica de canción ({duration}s)')

        categories = video_info.get('categories', [])
        if isinstance(categories, list):
            for cat in categories:
                if cat and cat.lower() in self.MUSIC_CATEGORIES:
                    score += 5
                    reasons.append(f'Categoría YouTube: {cat}')
                    break

        category_str = video_info.get('category', '')
        if category_str and category_str.lower() in self.MUSIC_CATEGORIES:
            score += 5
            reasons.append(f'Categoría YouTube: {category_str}')

        is_music = score >= 5
        confidence = self._get_confidence(score)

        suggested_artist = video_info.get('artist') or video_info.get('uploader', '')
        suggested_album = video_info.get('album') or ''

        return {
            'is_music': is_music,
            'confidence': confidence,
            'score': score,
            'reasons': reasons if reasons else ['Sin señales claras'],
            'suggested_artist': suggested_artist,
            'suggested_album': suggested_album,
        }

    def _get_confidence(self, score: int) -> str:
        if score >= 6:
            return 'high'
        elif score >= 3:
            return 'medium'
        else:
            return 'low'
