# Video Downloader API

## Visión General

`VideoDownloader` es un wrapper de yt-dlp para descargar videos completos en formato MP4. Maneja merge automático de video + audio y selección de resolución.

## Clase

```python
from core.video_downloader import VideoDownloader

config = {
    'non_music_output_dir': '~/Downloads/TubeToAlbum',
    'video_quality': '720',
    'quiet': True,
}
downloader = VideoDownloader(config)
```

## Constructor

### Parámetros de Configuración

```python
config = {
    'non_music_output_dir': '~/Downloads/TubeToAlbum',  # Carpeta base
    'non_music_video_subdir': 'Videos',                 # Subcarpeta (default: 'Videos')
    'output_template': '%(uploader)s/%(title)s.%(ext)s', # Template del nombre
    'video_quality': '720',                              # 360|480|720|1080|best
    'quiet': True,                                       # Silenciar output
}
```

## Métodos

### get_info(url)

Obtiene información del video sin descargarlo.

**Parámetros:**
- `url` (str): URL del video de YouTube

**Retorna:**
```python
{
    'title': 'Video Title',
    'artist': 'Channel Name',
    'uploader': 'Channel Name',
    'album': None,
    'thumbnail': 'https://...',
    'duration': 300,
    'upload_date': '20260101',
    'track_number': None,
    'description': 'Video description...',
    'categories': ['Entertainment']
}
```

**Excepciones:**
- `Exception`: Si falla la extracción de información

---

### download(url, progress_callback=None)

Descarga el video completo en MP4.

**Parámetros:**
- `url` (str): URL del video de YouTube
- `progress_callback` (Callable, opcional): Función de progreso

**progress_callback format:**
```python
def my_callback(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
    elif d['status'] == 'finished':
        print("Completado")
```

**Retorna:**
- `str`: Ruta del archivo descargado (o None)

## Opciones de yt-dlp

```python
{
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/best',
    'merge_output_format': 'mp4',
    'outtmpl': '~/Downloads/TubeToAlbum/Videos/%(uploader)s/%(title)s.%(ext)s',
    'progress_hooks': [callback],
    'quiet': True,
    'no_warnings': True,
    'restrictfilenames': True,
}
```

### Formato seleccionado

El formato usa una cadena de fallback:
1. `bestvideo[ext=mp4]+bestaudio[ext=m4a]` - Mejor video MP4 + mejor audio M4A
2. `bestvideo[ext=mp4]+bestaudio` - Mejor video MP4 + mejor audio (cualquier formato)
3. `best[ext=mp4]` - Mejor video+audio combinado en MP4
4. `best` - Lo mejor disponible

## Ejemplo de Uso

### Uso básico
```python
from core.video_downloader import VideoDownloader

config = {
    'non_music_output_dir': '~/Downloads/TubeToAlbum',
    'video_quality': '720',
    'quiet': True,
}

downloader = VideoDownloader(config)
info = downloader.get_info('https://youtube.com/watch?v=...')
print(f"Descargando: {info['title']}")
downloader.download('https://youtube.com/watch?v=...')
```

### Con callback de progreso
```python
def progress(d):
    if d['status'] == 'downloading':
        print(f"Progreso: {d.get('_percent_str', '0%')}")

downloader = VideoDownloader(config)
downloader.download(url, progress_callback=progress)
```

## Diferencias con TubeToAlbumDownloader

| Característica | TubeToAlbumDownloader | VideoDownloader |
|----------------|----------------------|-----------------|
| Formato salida | MP3, M4A | MP4 |
| Postprocessors | FFmpegExtractAudio, Metadata, EmbedThumbnail | Ninguno |
| Calidad | 128-320 kbps | 360p-1080p |
| Metadata | Sí (ID3 tags) | No |
| Portada | Sí (APIC) | No |
| Organización | Artista/Álbum/ | Videos/Canal/ |
