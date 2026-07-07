# Requisitos Previos

## Software Necesario

### Python 3.10 o superior
```bash
# Verificar versión
python --version
# Debe mostrar: Python 3.10.x o superior
```

### FFmpeg
FFmpeg es necesario para la conversión de audio.

**Instalación en Windows:**
```bash
# Opción 1: Chocolatey
choco install ffmpeg

# Opción 2: Scoop
scoop install ffmpeg

# Opción 3: Descarga manual
# Descargar desde https://ffmpeg.org/download.html
# Agregar al PATH del sistema
```

**Instalación en macOS:**
```bash
# Homebrew
brew install ffmpeg
```

**Instalación en Linux:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### Verificar FFmpeg
```bash
ffmpeg -version
# Debe mostrar información de la versión
```

## Dependencias de Python

Las dependencias se instalan con pip (ver Guía de Instalación).

| Paquete | Versión Mínima | Propósito |
|---------|---------------|-----------|
| yt-dlp | 2026.1.0 | Motor de descarga |
| mutagen | 1.47.0 | Escritura de metadata ID3 |
| Pillow | 10.0.0 | Procesamiento de imágenes |
| requests | 2.31.0 | HTTP requests |
| PySide6 | 6.6.0 | GUI (opcional) |

## Espacio en Disco
- **Mínimo**: 500 MB para la instalación
- **Recomendado**: 10 GB+ para biblioteca de música
- **Por canción MP3**: ~1-3 MB dependiendo de calidad

## Conexión a Internet
- Necesaria para descargar de YouTube
- No necesaria para reproducir archivos descargados

## Sistema Operativo
- **Windows**: 10 o superior
- **macOS**: 10.15 (Catalina) o superior
- **Linux**: Cualquier distribución moderna
