# Content Detector API

## Visión General

`ContentDetector` analiza información de un video de YouTube para determinar si es contenido musical o no-música. Usa un sistema de score basado en múltiples factores.

## Clase

```python
from core.content_detector import ContentDetector

detector = ContentDetector()
analysis = detector.detect(video_info)
```

## Método detect(video_info)

### Parámetros

`video_info` (dict): Información del video extraída por yt-dlp.

```python
video_info = {
    'title': 'Bohemian Rhapsody (Official Video Remastered)',
    'artist': 'Queen',           # Opcional
    'uploader': 'Queen Official',
    'album': 'A Night at the Opera',  # Opcional
    'track_number': 1,           # Opcional
    'playlist': 'Queen - Greatest Hits',  # Opcional
    'duration': 354,
    'categories': ['Music'],
    'category': 'Music',
}
```

### Retorna

```python
{
    'is_music': True,           # True si score >= 5
    'confidence': 'high',       # 'high' | 'medium' | 'low'
    'score': 8,                 # Puntuación total
    'reasons': [                # Lista de razones
        'Tiene artista: Queen',
        'Tiene álbum: A Night at the Opera',
        'Título contiene patrón musical',
        'Categoría YouTube: Music'
    ],
    'suggested_artist': 'Queen',
    'suggested_album': 'A Night at the Opera'
}
```

## Sistema de Score

### Factores que suman puntos

| Factor | Puntos | Ejemplo |
|--------|--------|---------|
| Tiene artista + álbum | +6 | `artist: "Queen"`, `album: "A Night at the Opera"` |
| Solo tiene artista | +1 | `artist: "Queen"` |
| Tiene número de pista | +2 | `track_number: 1` |
| Está en playlist | +3 | `playlist: "Queen - Greatest Hits"` |
| Patrón musical en título | +4 | "Official Video", "Lyrics", "Acoustic" |
| Duración típica de canción | +1 | 120-420 segundos |
| Categoría YouTube musical | +5 | `categories: ["Music"]` |

### Factores que restan puntos

| Factor | Puntos | Ejemplo |
|--------|--------|---------|
| Patrón de no-música en título | -4 | "Tutorial", "How to", "Vlog", "Podcast" |

### Confianza

| Score | Confianza |
|-------|-----------|
| ≥ 6 | `high` |
| 3-5 | `medium` |
| < 3 | `low` |

## Patrones de Título Musical

```python
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
```

## Patrones de No-Música

```python
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
```

## Ejemplos

### Video musical claro
```python
info = {
    'title': 'Bohemian Rhapsody (Official Video)',
    'artist': 'Queen',
    'album': 'A Night at the Opera',
    'categories': ['Music'],
    'duration': 354
}
# → is_music=True, score=13, confidence='high'
```

### Tutorial
```python
info = {
    'title': 'How to Learn Python - Full Tutorial',
    'uploader': 'Tech With Tim',
    'categories': ['Education'],
    'duration': 3600
}
# → is_music=False, score=0, confidence='low'
```

### Ambiguo
```python
info = {
    'title': 'Random Video',
    'uploader': 'Some Channel',
    'categories': ['Entertainment'],
    'duration': 300
}
# → is_music=False, score=5, confidence='medium'
```
