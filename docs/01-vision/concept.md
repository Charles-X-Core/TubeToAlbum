# Concepto

## Nombre
**TubeToAlbum**

## Definición
TubeToAlbum es un descargador profesional de YouTube con interfaz gráfica Electron y backend Python. Descarga audio como MP3 con metadata completa, portadas embebidas y organización en carpetas. También soporta descarga de video MP4.

## Arquitectura
- **Frontend**: Electron con HTML/CSS/JS y Tailwind CSS
- **Backend**: API REST Flask en Python
- **Core**: yt-dlp para descargas, Mutagen para metadata, Pillow para imágenes

## Propósito
- Descargar canciones y playlists de YouTube como MP3
- Descargar videos completos como MP4
- Guardar metadata completa (artista, título, álbum, año, género)
- Embeber portadas/thumbnails en los archivos
- Organizar automáticamente en carpetas: `Artista/Álbum/Título.mp3`
- Detectar contenido musical vs no-música automáticamente
- Funcionar sin conexión después de la descarga

## Casos de Uso
1. Descargar una canción suelta de YouTube
2. Descargar un álbum completo (playlist de YouTube)
3. Descargar toda la discografía de un artista
4. Guardar música para escuchar offline en cualquier reproductor
5. Crear una biblioteca musical organizada desde YouTube
6. Descargar videos de YouTube como MP4
7. Descargar contenido de YouTube Music

## Filosofía
- **Simplicidad**: Interfaz intuitiva con un solo clic
- **Calidad**: Mejor calidad de audio posible desde YouTube
- **Organización**: Archivos siempre bien nombrados y organizados
- **Portabilidad**: Funciona en Windows, macOS y Linux
- **Modernidad**: UI glassmorphism con animaciones suaves
