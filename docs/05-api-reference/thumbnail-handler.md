# Thumbnail Handler API

## Clase ThumbnailHandler

```python
class ThumbnailHandler:
    """Manejador de portadas/thumbnails."""
    
    YOUTUBE_THUMBNAIL_URLS = {
        'maxresdefault': 'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg',
        'sddefault': 'https://img.youtube.com/vi/{video_id}/sddefault.jpg',
        'hqdefault': 'https://img.youtube.com/vi/{video_id}/hqdefault.jpg',
        'mqdefault': 'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
        'default': 'https://img.youtube.com/vi/{video_id}/default.jpg',
    }
    
    def __init__(self):
        """Inicializar handler."""
        self.session = requests.Session()
    
    def get_video_id(self, url):
        """
        Extraer video ID de una URL de YouTube.
        
        Args:
            url: URL del video
            
        Returns:
            str: Video ID
        """
        # youtube.com/watch?v=VIDEO_ID
        # youtu.be/VIDEO_ID
        # youtube.com/embed/VIDEO_ID
        patterns = [
            r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def download_thumbnail(self, video_id, quality='maxresdefault'):
        """
        Descargar thumbnail de YouTube.
        
        Args:
            video_id: ID del video
            quality: Calidad del thumbnail
            
        Returns:
            bytes: Datos de la imagen o None
        """
        url = self.YOUTUBE_THUMBNAIL_URLS.get(quality)
        if not url:
            return None
        
        url = url.format(video_id=video_id)
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except:
            pass
        
        return None
    
    def download_best_thumbnail(self, video_id):
        """
        Descargar mejor thumbnail disponible.
        
        Args:
            video_id: ID del video
            
        Returns:
            bytes: Datos de la imagen
        """
        qualities = ['maxresdefault', 'sddefault', 'hqdefault', 'mqdefault']
        
        for quality in qualities:
            data = self.download_thumbnail(video_id, quality)
            if data:
                return data
        
        return None
    
    def resize_image(self, image_data, max_size=(500, 500)):
        """
        Redimensionar imagen.
        
        Args:
            image_data: Datos binarios de la imagen
            max_size: Tamaño máximo (ancho, alto)
            
        Returns:
            bytes: Datos de la imagen redimensionada
        """
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85)
        return output.getvalue()
    
    def save_thumbnail(self, image_data, filepath):
        """
        Guardar thumbnail en disco.
        
        Args:
            image_data: Datos binarios de la imagen
            filepath: Ruta donde guardar
        """
        with open(filepath, 'wb') as f:
            f.write(image_data)
```

## Métodos

### get_video_id(url)
Extrae el video ID de una URL de YouTube.

### download_thumbnail(video_id, quality)
Descarga un thumbnail específico.

### download_best_thumbnail(video_id)
Descarga la mejor calidad disponible automáticamente.

### resize_image(image_data, max_size)
Redimensiona una imagen.

### save_thumbnail(image_data, filepath)
Guarda el thumbnail en disco.

## Calidades Disponibles

| Calidad | Resolución | Uso |
|---------|-----------|-----|
| maxresdefault | 1920x1080 | Máxima calidad |
| sddefault | 640x480 | Calidad estándar |
| hqdefault | 480x360 | Alta calidad |
| mqdefault | 320x180 | Calidad media |
| default | 120x90 | Baja calidad |

## Uso

```python
handler = ThumbnailHandler()

# Descargar mejor thumbnail
video_id = handler.get_video_id("https://youtube.com/watch?v=fJ9rUzIMcZQ")
thumbnail = handler.download_best_thumbnail(video_id)

# Redimensionar
thumbnail = handler.resize_image(thumbnail, max_size=(500, 500))

# Guardar
handler.save_thumbnail(thumbnail, 'cover.jpg')
```
