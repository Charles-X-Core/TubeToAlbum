# yt-dlp Wrapper API

## Clase Downloader

```python
class TubeToAlbumDownloader:
    """Wrapper de yt-dlp para TubeToAlbum."""
    
    def __init__(self, config):
        """
        Inicializar downloader.
        
        Args:
            config: Configuración del usuario
        """
        self.config = config
        self.ydl_opts = self._build_options()
    
    def _build_options(self):
        """Construir opciones de yt-dlp."""
        return {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': self.config['format'],
                    'preferredquality': self.config['quality'],
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
                {
                    'key': 'EmbedThumbnail',
                },
            ],
            'writethumbnail': True,
            'outtmpl': self.config['output_template'],
            'progress_hooks': [self._progress_hook],
        }
    
    def get_info(self, url):
        """
        Obtener información del video sin descargar.
        
        Args:
            url: URL del video de YouTube
            
        Returns:
            dict: Información del video
        """
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return self._parse_info(info)
    
    def download(self, url):
        """
        Descargar audio del video.
        
        Args:
            url: URL del video de YouTube
            
        Returns:
            str: Ruta del archivo descargado
        """
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([url])
    
    def download_playlist(self, playlist_url):
        """
        Descargar playlist completa.
        
        Args:
            playlist_url: URL de la playlist
            
        Returns:
            list: Lista de rutas de archivos descargados
        """
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            ydl.download([playlist_url])
    
    def _progress_hook(self, d):
        """Callback de progreso."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"\r{percent} | Speed: {speed} | ETA: {eta}", end='')
        elif d['status'] == 'finished':
            print("\nDownload complete!")
    
    def _parse_info(self, info):
        """Parsear información del video."""
        return {
            'title': info.get('title'),
            'artist': info.get('artist') or info.get('uploader'),
            'album': info.get('album') or info.get('playlist'),
            'thumbnail': info.get('thumbnail'),
            'duration': info.get('duration'),
            'upload_date': info.get('upload_date'),
            'track_number': info.get('track_number') or info.get('playlist_index'),
            'description': info.get('description'),
        }
```

## Métodos Principales

### get_info(url)
Obtiene metadata del video sin descargarlo.

**Retorna:**
```python
{
    'title': 'Bohemian Rhapsody',
    'artist': 'Queen',
    'album': 'A Night at the Opera',
    'thumbnail': 'https://img.youtube.com/vi/.../maxresdefault.jpg',
    'duration': 354,
    'upload_date': '19751031',
    'track_number': 5,
    'description': '...'
}
```

### download(url)
Descarga y convierte el audio a MP3.

**Parámetros:**
- `url` (str): URL del video

### download_playlist(url)
Descarga una playlist completa.

**Parámetros:**
- `url` (str): URL de la playlist

## Configuración

```python
config = {
    'quality': '192',           # 128, 192, 256, 320
    'format': 'mp3',            # mp3, m4a, flac
    'output_template': '%(artist|uploader)s/%(album|playlist)s/%(track_number)02d - %(title)s.%(ext)s',
    'embed_metadata': True,
    'embed_thumbnail': True,
}

downloader = TubeToAlbumDownloader(config)
```
