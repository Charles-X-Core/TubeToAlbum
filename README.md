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
git clone https://github.com/Charles-X-Core/TubeToAlbum.git
cd TubeToAlbum

# Instalar dependencias Python
pip install -r requirements.txt
pip install -r backend/requirements.txt

# Instalar dependencias Electron
cd electron && npm install && cd ..
```

### Ejecutar (Desarrollo)
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

## 📦 Instalación Rápida (Windows - Installer)

### Descargar Installer
- **GitHub Releases**: [Descargar `TubeToAlbum Setup 1.0.0.exe`](https://github.com/Charles-X-Core/TubeToAlbum/releases/latest)
- Tamaño: ~80 MB
- Incluye: Python 3.11 embebido, FFmpeg, Electron, dependencias

### Instalar
1. Ejecuta `TubeToAlbum Setup 1.0.0.exe`
2. Sigue el asistente (NSIS - instala por usuario o sistema)
3. Lanza desde **Inicio → TubeToAlbum** o acceso directo en Escritorio

### Desinstalar
- Panel de Control → Programas → TubeToAlbum → Desinstalar
- O ejecuta `uninstall.exe` en la carpeta de instalación

---

## 🏗️ Build & Distribución (Electron)

### Estructura de Build
```
electron/
├── dist/
│   ├── win-unpacked/          # App portable (sin installer)
│   │   ├── TubeToAlbum.exe    # Ejecutable principal (~177 MB)
│   │   ├── resources/
│   │   │   ├── backend/       # Python API (Flask)
│   │   │   ├── core/          # Módulos Python
│   │   │   └── utils/
│   │   └── locales/
│   └── TubeToAlbum Setup 1.0.0.exe   # Installer NSIS (~80 MB)
├── package.json               # Config Electron + electron-builder
├── main.js                    # Entry point + spawn backend
├── preload.js                 # IPC bridge
├── renderer/                  # UI (HTML/CSS/JS + Tailwind)
│   ├── index.html
│   ├── app.js
│   └── styles.css
└── assets/
    ├── icon.ico               # Icono app (256x256)
    └── installer_header.png   # Header installer (493x58) "by Charles-X-Core"
```

### Comandos Build
```bash
cd electron

# Build desarrollo (desempaquetado)
npm run build:dir

# Build producción + installer NSIS
npm run build

# Solo empaquetar (sin installer)
npm run build:dir
```

### Configuración electron-builder (`package.json`)
```json
{
  "build": {
    "appId": "com.tubetoalbum.app",
    "productName": "TubeToAlbum",
    "directories": { "output": "dist" },
    "files": ["main.js", "preload.js", "renderer/**/*", "assets/**/*"],
    "extraResources": [
      { "from": "../backend", "to": "backend" },
      { "from": "../core", "to": "core" },
      { "from": "../utils", "to": "utils" },
      { "from": "../requirements.txt", "to": "requirements.txt" },
      { "from": "../config.json", "to": "config.json" }
    ],
    "win": {
      "target": [{ "target": "nsis", "arch": ["x64"] }],
      "icon": "assets/icon.ico"
    },
    "nsis": {
      "oneClick": false,
      "allowToChangeInstallationDirectory": true,
      "installerIcon": "assets/icon.ico",
      "uninstallerIcon": "assets/icon.ico",
      "installerHeaderIcon": "assets/installer_header.png",
      "createDesktopShortcut": true,
      "createStartMenuShortcut": true,
      "shortcutName": "TubeToAlbum"
    }
  }
}
```

### Detalles Técnicos del Build
- **Electron**: v28.3.3
- **electron-builder**: v24.13.3
- **Target**: NSIS (x64) - Windows 10/11
- **Arquitectura**: x64
- **Python embebido**: 3.11 (incluido en resources/backend)
- **FFmpeg**: Embebido en backend Python
- **Tamaño installer**: ~80 MB (comprimido NSIS)
- **Tamaño unpacked**: ~177 MB

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
# 139 tests passing
```
