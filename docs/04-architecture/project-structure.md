# Estructura del Proyecto

```
TubeToAlbum/
│
├── README.md                        # Documentación principal
├── requirements.txt                 # Dependencias Python (yt-dlp, mutagen, Pillow, flask)
├── config.json                      # Configuración por defecto
├── history.json                     # Historial de descargas (persistente)
├── start.bat                        # Launcher Windows (backend + Electron)
│
├── core/                            # Motor de descarga y procesamiento
│   ├── __init__.py
│   ├── downloader.py                # Wrapper yt-dlp para audio (MP3/M4A)
│   ├── video_downloader.py          # Wrapper yt-dlp para video (MP4)
│   ├── content_detector.py          # Detección música vs no-música
│   ├── metadata.py                  # Escritura de tags ID3 (Mutagen)
│   ├── parser.py                    # Parseo inteligente de títulos
│   ├── thumbnail.py                 # Descarga y procesamiento de portadas
│   └── organizer.py                 # Organización de archivos en carpetas
│
├── backend/                         # API REST Flask
│   ├── server.py                    # Servidor Flask con endpoints
│   └── requirements.txt             # Dependencias del backend (flask, flask-cors)
│
├── electron/                        # Aplicación de escritorio Electron
│   ├── package.json                 # Manifest de npm
│   ├── main.js                      # Main process (BrowserWindow, IPC)
│   ├── preload.js                   # Bridge seguro (contextBridge)
│   └── renderer/                    # Frontend UI
│       ├── index.html               # Layout principal
│       ├── app.js                   # Lógica de la aplicación
│       └── styles.css               # Estilos glassmorphism
│
├── gui/                             # GUI PySide6 (LEGACY - en desuso)
│   ├── __init__.py
│   ├── main_window.py               # Ventana principal Qt
│   ├── download_worker.py           # Workers QThread
│   ├── history_tab.py               # Tab de historial
│   ├── settings_tab.py              # Tab de configuración
│   ├── run.py                       # Entry point Qt
│   └── custom.css                   # Overrides CSS
│
├── cli/                             # Interfaz de línea de comandos
│   ├── __init__.py
│   └── main.py                      # CLI con argparse + prompts interactivos
│
├── utils/                           # Utilidades compartidas
│   ├── __init__.py
│   ├── config_utils.py              # Gestión de configuración
│   ├── file_utils.py                # Utilidades de archivos
│   └── url_utils.py                 # Validación y sanitización de URLs
│
├── tests/                           # Tests unitarios (pytest)
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_video_downloader.py
│   ├── test_content_detector.py
│   ├── test_metadata.py
│   ├── test_parser.py
│   ├── test_thumbnail.py
│   ├── test_organizer.py
│   ├── test_config_utils.py
│   ├── test_file_utils.py
│   └── test_url_utils.py
│
└── docs/                            # Documentación
    ├── 01-vision/
    │   ├── concept.md
    │   └── features.md
    ├── 02-installation/
    │   ├── requirements.md
    │   └── installation.md
    ├── 03-usage/
    │   ├── cli-usage.md
    │   ├── gui-usage.md
    │   └── examples.md
    ├── 04-architecture/
    │   ├── project-structure.md      # Este archivo
    │   ├── download-flow.md
    │   ├── metadata-handling.md
    │   └── electron-architecture.md
    └── 05-api-reference/
        ├── ytdlp-wrapper.md
        ├── backend-api.md
        ├── content-detector.md
        ├── video-downloader.md
        ├── metadata-writer.md
        └── thumbnail-handler.md
```

## Descripción de Módulos

### core/downloader.py
Motor principal de descarga de audio. Wrapper de yt-dlp con:
- Descarga de audio individual (MP3, M4A)
- Selección de calidad (128-320 kbps)
- Callbacks de progreso en tiempo real
- Construcción manual de rutas de salida (evita bugs de yt-dlp en Windows)
- Postprocessors: FFmpegExtractAudio, FFmpegMetadata, EmbedThumbnail

### core/video_downloader.py
Motor de descarga de video completo. Wrapper de yt-dlp con:
- Descarga de video MP4
- Selección de resolución (360p-1080p)
- Merge automático de video + audio
- Progreso en tiempo real

### core/content_detector.py
Sistema de detección de contenido musical:
- Score basado en: título, categorías, duración, playlists
- Patrones: "Official Video", "Lyrics", "Audio", "Album"
- Threshold configurable (≥5 = música)
- Retorna: is_music, score, reasons, suggested_artist

### core/metadata.py
Escritura de tags ID3 en archivos MP3 usando Mutagen:
- Tags básicos (título, artista, álbum)
- Tags extendidos (año, género, número de pista)
- Embebed de portada (APIC)
- Soporte para M4A y FLAC

### core/parser.py
Parseo inteligente de títulos de YouTube:
- Detección de "Artista - Título"
- Limpieza de suffixes (Official Video, HD, Lyrics, etc.)
- Manejo de feat./ft.
- Fallback a uploader

### core/thumbnail.py
Gestión de portadas/thumbnails:
- Descarga desde YouTube (múltiples calidades)
- Redimensionamiento con Pillow
- Conversión de formato
- Embebed en MP3

### core/organizer.py
Organización de archivos en carpetas:
- Creación de estructura Artista/Álbum/
- Naming de archivos
- Manejo de duplicados con contador
- Configuración de templates

### backend/server.py
API REST Flask para Electron:
- `/api/info` - Información del video
- `/api/download` - Iniciar descarga
- `/api/progress/<job_id>` - Progreso de descarga
- `/api/cancel/<job_id>` - Cancelar descarga
- `/api/history` - Gestión de historial
- `/api/config` - Gestión de configuración
- Threading para descargas concurrentes
- Persistencia en history.json y config.json

### electron/main.js
Main process de Electron:
- Crea BrowserWindow con frameless titlebar
- Spawn del backend Python como child process
- Espera a que el backend esté listo antes de cargar UI
- Handlers IPC: minimize, maximize, close, select-folder

### electron/preload.js
Bridge seguro entre renderer y backend:
- contextBridge expone `window.api`
- Métodos: getInfo, startDownload, getProgress, cancelDownload
- Historial: getHistory, clearHistory, deleteHistoryEntry
- Config: getConfig, saveConfig
- Ventana: minimizeWindow, maximizeWindow, closeWindow
- Sistema de archivos: selectFolder, openFolder
