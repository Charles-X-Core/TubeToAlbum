# Manejo de Metadata

## Flujo de Metadata

```
Video de YouTube
    │
    ▼
yt-dlp extrae información:
    ├── title: "Queen - Bohemian Rhapsody (Official Video)"
    ├── artist: (no disponible directamente)
    ├── uploader: "Queen Official"
    ├── album: (no disponible)
    ├── upload_date: "20080801"
    ├── thumbnail: "https://img.youtube.com/vi/.../maxresdefault.jpg"
    └── duration: 354
    │
    ▼
Parser procesa el título:
    ├── Limpia: "Queen - Bohemian Rhapsody"
    ├── Detecta separador " - "
    ├── Extrae: artist="Queen", title="Bohemian Rhapsody"
    └── Fallback: artist="Queen Official" si no detecta
    │
    ▼
Metadata final lista:
    ├── Título: "Bohemian Rhapsody"
    ├── Artista: "Queen"
    ├── Álbum: (de playlist o "Unknown Album")
    ├── Año: "1975" (extraído de upload_date)
    ├── Género: "Music" (categoría de YouTube)
    ├── Número de pista: (de playlist_index)
    └── Portada: (thumbnail URL)
    │
    ▼
Mutagen escribe en el MP3:
    ├── TIT2 = "Bohemian Rhapsody"
    ├── TPE1 = "Queen"
    ├── TALB = "A Night at the Opera"
    ├── TDRC = "1975"
    ├── TCON = "Music"
    ├── TRCK = "5"
    └── APIC = (imagen JPEG)
```

## Prioridad de Campos

### Artista
1. `artist` (si YouTube lo provee - videos musicales)
2. Parseo del título ("Artist - Title")
3. `uploader` (nombre del canal)
4. "Unknown Artist" (fallback)

### Álbum
1. `album` (si YouTube lo provee)
2. `playlist_title` (título de la playlist)
3. "Unknown Album" (fallback)

### Año
1. `upload_date` (extraer YYYY)
2. Año actual (fallback)

### Género
1. `categories[0]` (primera categoría de YouTube)
2. "Music" (fallback)

### Número de Pista
1. `track_number` (si YouTube lo provee)
2. `playlist_index` (posición en playlist)
3. 0 (fallback)

## Formato de Archivos de Metadata

### config.json
```json
{
  "metadata": {
    "embed_thumbnail": true,
    "embed_metadata": true,
    "default_genre": "Music",
    "default_album": "Unknown Album",
    "default_artist": "Unknown Artist",
    "clean_title": true,
    "title_patterns_to_remove": [
      "\\(?Official(Music)?Video\\)?",
      "\\[?Official(Music)?Video\\]?",
      "\\(?Official Audio\\)?",
      "\\(?Audio\\)?",
      "\\(?Video\\)?",
      "\\[?HD\\]?",
      "\\[?4K\\]?",
      "\\[?Lyrics\\]?",
      "\\(?Lyrics\\)?"
    ]
  }
}
```

## Tags ID3 Soportados

| Tag | Campo | Descripción |
|-----|-------|-------------|
| TIT2 | title | Título de la canción |
| TPE1 | artist | Artista principal |
| TALB | album | Nombre del álbum |
| TRCK | track_number | Número de pista |
| TDRC | year | Año de grabación |
| TCON | genre | Género musical |
| TPE2 | album_artist | Artista del álbum |
| TCOM | composer | Compositor |
| COMM | comment | Comentario |
| APIC | thumbnail | Portada (imagen) |

## Ejemplo de Escritura con Mutagen

```python
from mutagen.id3 import ID3, TPE1, TIT2, TALB, TRCK, TDRC, TCON, APIC
from mutagen.mp3 import MP3

def write_metadata(filepath, metadata):
    audio = MP3(filepath, ID3=ID3)
    
    try:
        audio.add_tags()
    except:
        pass
    
    # Tags básicos
    audio.tags.add(TIT2(encoding=3, text=metadata['title']))
    audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
    audio.tags.add(TALB(encoding=3, text=metadata['album']))
    audio.tags.add(TRCK(encoding=3, text=str(metadata['track'])))
    audio.tags.add(TDRC(encoding=3, text=str(metadata['year'])))
    audio.tags.add(TCON(encoding=3, text=metadata['genre']))
    
    # Portada
    if metadata.get('thumbnail_data'):
        audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc='Cover',
            data=metadata['thumbnail_data']
        ))
    
    audio.save()
```
