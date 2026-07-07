# Guía de Instalación

## Opción 1: Instalación desde Código Fuente

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/TubeToAlbum.git
cd TubeToAlbum
```

### 2. Crear entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Verificar instalación
```bash
python -m cli.main --help
```

## Opción 2: Instalación Directa con pip (Futuro)

```bash
pip install tubetoalbum
```

## Opción 3: Ejecutable Standalone (Futuro)

Descargar el `.exe` desde la página de releases.

## Configuración Inicial

### Archivo de configuración
Se crea automáticamente en `~/.tubetoalbum/config.json`:

```json
{
  "default_quality": "192",
  "default_format": "mp3",
  "output_template": "%(artist|uploader)s/%(album|playlist)s/%(track_number)02d - %(title)s.%(ext)s",
  "default_output_dir": "~/Music",
  "embed_metadata": true,
  "embed_thumbnail": true,
  "overwrite_existing": false
}
```

### Editar configuración
```bash
# Abrir en editor por defecto
tube2album --config
```

## Solución de Problemas

### FFmpeg no encontrado
```
Error: FFmpeg not found
```
**Solución**: Asegurar que FFmpeg está instalado y en el PATH.

### Error de permisos
```
PermissionError: [Errno 13] Permission denied
```
**Solución**: Ejecutar como administrador o cambiar carpeta de salida.

### yt-dlp desactualizado
```
Error: YouTube returned an error
```
**Solución**:
```bash
pip install --upgrade yt-dlp
```
