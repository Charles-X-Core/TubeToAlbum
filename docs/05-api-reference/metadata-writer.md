# Metadata Writer API

## Clase MetadataWriter

```python
class MetadataWriter:
    """Escritor de metadata ID3 para archivos MP3."""
    
    def __init__(self, filepath):
        """
        Inicializar writer.
        
        Args:
            filepath: Ruta del archivo MP3
        """
        self.filepath = filepath
        self.audio = MP3(filepath, ID3=ID3)
        
        if self.audio.tags is None:
            self.audio.add_tags()
    
    def write_basic(self, title, artist, album):
        """
        Escribir tags básicos.
        
        Args:
            title: Título de la canción
            artist: Nombre del artista
            album: Nombre del álbum
        """
        self.audio.tags.add(TIT2(encoding=3, text=title))
        self.audio.tags.add(TPE1(encoding=3, text=artist))
        self.audio.tags.add(TALB(encoding=3, text=album))
    
    def write_extended(self, track_number=None, year=None, genre=None):
        """
        Escribir tags extendidos.
        
        Args:
            track_number: Número de pista (opcional)
            year: Año de grabación (opcional)
            genre: Género musical (opcional)
        """
        if track_number:
            self.audio.tags.add(TRCK(encoding=3, text=str(track_number)))
        if year:
            self.audio.tags.add(TDRC(encoding=3, text=str(year)))
        if genre:
            self.audio.tags.add(TCON(encoding=3, text=genre))
    
    def write_thumbnail(self, thumbnail_data):
        """
        Embeber portada en el MP3.
        
        Args:
            thumbnail_data: Datos binarios de la imagen (JPEG)
        """
        self.audio.tags.add(APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,  # Cover (front)
            desc='Cover',
            data=thumbnail_data
        ))
    
    def write_all(self, metadata):
        """
        Escribir metadata completa.
        
        Args:
            metadata: Diccionario con toda la metadata
        """
        self.write_basic(
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album']
        )
        
        self.write_extended(
            track_number=metadata.get('track_number'),
            year=metadata.get('year'),
            genre=metadata.get('genre')
        )
        
        if metadata.get('thumbnail_data'):
            self.write_thumbnail(metadata['thumbnail_data'])
    
    def save(self):
        """Guardar cambios en el archivo (ID3v2.3 para compatibilidad)."""
        self.audio.save(v2_version=3)
    
    def read(self):
        """
        Leer metadata del archivo.
        
        Returns:
            dict: Metadata del archivo
        """
        return {
            'title': str(self.audio.tags.get('TIT2', '')),
            'artist': str(self.audio.tags.get('TPE1', '')),
            'album': str(self.audio.tags.get('TALB', '')),
            'track_number': str(self.audio.tags.get('TRCK', '')),
            'year': str(self.audio.tags.get('TDRC', '')),
            'genre': str(self.audio.tags.get('TCON', '')),
        }
```

## Métodos

### write_basic(title, artist, album)
Escribe los tags básicos obligatorios.

### write_extended(track_number, year, genre)
Escribe tags opcionales.

### write_thumbnail(thumbnail_data)
Embebe una imagen como portada.

### write_all(metadata)
Escribe toda la metadata de una vez.

### save()
Guarda los cambios en el archivo.

### read()
Lee la metadata existente del archivo.

## Uso

```python
writer = MetadataWriter('song.mp3')

writer.write_all({
    'title': 'Bohemian Rhapsody',
    'artist': 'Queen',
    'album': 'A Night at the Opera',
    'track_number': 5,
    'year': 1975,
    'genre': 'Rock',
    'thumbnail_data': thumbnail_bytes
})

writer.save()
```
