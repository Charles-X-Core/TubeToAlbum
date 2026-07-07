# Uso CLI

## Comandos Principales

### Descargar un Video
```bash
tube2album [URL]
```

Ejemplo:
```bash
tube2album "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"
```

### Descargar con Calidad Específica
```bash
tube2album [URL] -q [CALIDAD]
```

Ejemplo:
```bash
tube2album "https://www.youtube.com/watch?v=fJ9rUzIMcZQ" -q 320
```

### Descargar a Carpeta Específica
```bash
tube2album [URL] -o [CARPETA]
```

Ejemplo:
```bash
tube2album "https://www.youtube.com/watch?v=fJ9rUzIMcZQ" -o "C:/Music/Queen"
```

### Descargar Playlist
```bash
tube2album [PLAYLIST_URL]
```

Ejemplo:
```bash
tube2album "https://www.youtube.com/playlist?list=PL..."
```

### Descargar sin Metadata
```bash
tube2album [URL] --no-metadata
```

### Descargar sin Portada
```bash
tube2album [URL] --no-thumbnail
```

## Opciones Disponibles

| Opción | Descripción | Por Defecto |
|--------|-------------|-------------|
| `-q, --quality` | Calidad MP3 (128/192/256/320) | 192 |
| `-o, --output` | Carpeta de salida | ~/Music |
| `-f, --format` | Formato de audio (mp3/m4a/flac) | mp3 |
| `--no-metadata` | No embeber metadata | false |
| `--no-thumbnail` | No embeber portada | false |
| `--overwrite` | Sobrescribir existentes | false |
| `-v, --verbose` | Modo detallado | false |
| `--config` | Abrir configuración | - |
| `-h, --help` | Mostrar ayuda | - |

## Modo Verbose

Para ver información detallada de la descarga:
```bash
tube2album [URL] -v
```

Salida ejemplo:
```
[INFO] Extracting info from: https://youtube.com/watch?v=...
[INFO] Title: Queen - Bohemian Rhapsody
[INFO] Artist: Queen
[INFO] Album: A Night at the Opera
[INFO] Duration: 354s
[INFO] Downloading audio...
[INFO] Converting to MP3 192kbps...
[INFO] Embedding metadata...
[INFO] Embedding thumbnail...
[INFO] Saved to: ~/Music/Queen/A Night at the Opera/01 - Bohemian Rhapsody.mp3
[INFO] Done!
```
