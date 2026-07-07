# Características

## Descarga de Audio
- Extraer audio de cualquier video de YouTube
- Soporte para playlists completas
- Soporte para canales completos
- Descarga múltiple en paralelo (configurable)
- Soporte para YouTube Music (`music.youtube.com`)

## Descarga de Video
- Descarga completa en MP4
- Selección de calidad: 360p, 480p, 720p, 1080p, mejor calidad
- Merge automático de video + audio

## Calidad de Audio
| Formato | Calidad | Tamaño aprox | Recomendación |
|---------|---------|--------------|---------------|
| MP3 128kbps | Estándar | ~1 MB/min | Ahorrar espacio |
| MP3 192kbps | Alta | ~1.5 MB/min | **Por defecto** |
| MP3 256kbps | Muy alta | ~2 MB/min | Calidad premium |
| MP3 320kbps | Máxima | ~2.5 MB/min | Máxima calidad |
| M4A 256kbps | Nativa YouTube | ~2 MB/min | Mejor fidelidad |

## Detección de Contenido
- Análisis automático: ¿es música o no-música?
- Score de confianza (high/medium/low)
- Detección basada en: título, categorías, duración, playlists
- Confirmación interactiva antes de descargar
- Para contenido no-música: preguntar si descargar MP3 o MP4

## Metadata
- **Título**: Extraído y limpiado del video de YouTube
- **Artista**: Parseado del título o uploader
- **Álbum**: De la playlist o video
- **Año**: Fecha de subida del video
- **Género**: Categorías de YouTube
- **Número de pista**: Índice en la playlist
- **Portada**: Thumbnail embebido como APIC

## Organización de Archivos
```
Music/
├── Queen/
│   ├── A Night at the Opera/
│   │   ├── Bohemian Rhapsody.mp3
│   │   └── ...
│   └── The Game/
│       └── Another One Bites the Dust.mp3
├── Led Zeppelin/
│   └── Led Zeppelin IV/
│       └── Stairway to Heaven.mp3
└── ...

Downloads/TubeToAlbum/    # Contenido no-música
├── Video Tutorial.mp4
└── ...
```

## Interfaz Gráfica (Electron)
- Title bar personalizado con controles de ventana (minimizar, maximizar, cerrar)
- Sidebar con navegación por tabs
- Tab Descargar: input URL, preview, opciones, progreso
- Tab Historial: tabla de descargas con eliminar
- Tab Configuración: calidad, formato, carpetas, metadata
- Quick paths para "Guardar en": Mi Música, Descargas, Escritorio, Personalizar
- Folder picker nativo del sistema operativo
- Toast notifications animados
- Modal de confirmación custom (sin `confirm()` nativo)
- Diseño glassmorphism con animaciones suaves
- Responsive y moderno

## Interfaz de Línea de Comandos (CLI)
- Descarga rápida con un comando
- Opciones de calidad configurables
- Carpeta de salida personalizable
- Modo verbose para debugging
- Detección interactiva de contenido
- Soporte para `--info`, `--yes`, `--mp4`, `--mp3`
