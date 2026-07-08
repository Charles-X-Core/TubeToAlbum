# TubeToAlbum

> Descargador profesional de YouTube a MP3/MP4 para PC con metadata completa, portadas embebidas (APIC + folder.jpg) y organización en carpetas.

---

## Inicio Rápido

### Requisitos
- Python 3.11+
- FFmpeg (agregado al PATH)
- Node.js 18+ (para Electron)

### Instalación
```bash
# Clonar
git clone https://github.com/tubetoalbum/tubetoalbum.git
cd tubetoalbum

# Instalar dependencias Python
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Instalar dependencias Electron
cd electron && npm install && cd ..
```

### Ejecutar
```bash
# Opción 1: Script automático (Windows)
start.bat

# Opción 2: Manual
# Terminal 1 - Backend
cd backend && python server.py

# Terminal 2 - Electron
cd electron && npm start
```

### CLI (sin GUI)
```bash
python cli/main.py "https://youtube.com/watch?v=..."
python cli/main.py "URL" --quality 320 --format mp3
python cli/main.py "URL" --mp4 -y
```

---

## Arquitectura

```
┌─────────────────────────┐     HTTP     ┌─────────────────────────┐
│   ELECTRON (Frontend)   │ ◄──────────► │   PYTHON (Backend)      │
│                         │  localhost   │                          │
│   Tailwind CSS          │    :5000     │   Flask API              │
│   HTML/CSS/JS           │              │   core/ modules          │
│   - Tab Descargar       │              │   - /api/info            │
│   - Tab Historial       │              │   - /api/download        │
│   - Tab Configuración   │              │   - /api/progress        │
└─────────────────────────┘              └─────────────────────────┘
```

---

## Índice de Documentación

### 1. Visión del Proyecto
- [Concepto](01-vision/concept.md)
- [Características](01-vision/features.md)

### 2. Instalación
- [Requisitos Previos](02-installation/requirements.md)
- [Guía de Instalación](02-installation/installation.md)

### 3. Uso
- [Modo CLI](03-usage/cli-usage.md)
- [Modo GUI (Electron)](03-usage/gui-usage.md)
- [Ejemplos](03-usage/examples.md)

### 4. Arquitectura
- [Estructura del Proyecto](04-architecture/project-structure.md)
- [Flujo de Descarga](04-architecture/download-flow.md)
- [Manejo de Metadata](04-architecture/metadata-handling.md)
- [Arquitectura Electron](04-architecture/electron-architecture.md)

### 5. Referencia API
- [yt-dlp Wrapper](05-api-reference/ytdlp-wrapper.md)
- [Backend API REST](05-api-reference/backend-api.md)
- [Content Detector](05-api-reference/content-detector.md)
- [Video Downloader](05-api-reference/video-downloader.md)
- [Metadata Writer](05-api-reference/metadata-writer.md)
- [Thumbnail Handler](05-api-reference/thumbnail-handler.md)

---

## Plataforma
Windows / macOS / Linux (Python 3.11+)

## Estado
Activo - v1.0.0

## Tests
```bash
python -m pytest tests/ --tb=short -q
# 114 tests passing
```
