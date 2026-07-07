# Backend API REST

## Visión General

El backend es un servidor Flask que expone una API REST para la aplicación Electron. Escucha en `http://127.0.0.1:5000`.

## Endpoints

### POST /api/info

Obtiene información de un video de YouTube y analiza si es música.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Response (200):**
```json
{
  "info": {
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "uploader": "Queen Official",
    "album": "A Night at the Opera",
    "thumbnail": "https://...",
    "duration": 354,
    "upload_date": "19751031",
    "url": "https://www.youtube.com/watch?v=..."
  },
  "analysis": {
    "is_music": true,
    "score": 8,
    "reasons": ["Official Video", "Music category"],
    "suggested_artist": "Queen"
  }
}
```

**Errors:**
- `400` - URL requerida o inválida
- `404` - No se pudo obtener información
- `500` - Error interno

---

### POST /api/download

Inicia una descarga en un hilo separado.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "format": "mp3",
  "quality": "192",
  "output_dir": "C:\\Music",
  "is_music": true
}
```

**Response (200):**
```json
{
  "job_id": "a1b2c3d4"
}
```

**Notes:**
- `format`: "mp3", "m4a", o "mp4"
- `quality`: "128", "192", "256", "320" (audio) o "360", "480", "720", "1080", "best" (video)
- `is_music`: determina si usar carpeta de música o downloads

---

### GET /api/progress/{job_id}

Obtiene el progreso de una descarga.

**Response (200):**
```json
{
  "status": "downloading",
  "progress": 65.3,
  "speed": "1.2MB/s",
  "eta": "00:12",
  "filepath": "",
  "error": ""
}
```

**Status posibles:**
- `downloading` - En progreso
- `completed` - Finalizado
- `error` - Error (ver `error`)
- `cancelled` - Cancelado

---

### POST /api/cancel/{job_id}

Cancela una descarga activa.

**Response (200):**
```json
{ "ok": true }
```

---

### GET /api/history

Obtiene el historial de descargas.

**Response (200):**
```json
[
  {
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "format": "MP3",
    "filepath": "C:\\Music\\Queen\\A Night at the Opera\\Bohemian Rhapsody.mp3",
    "date": "2026-07-05 22:30",
    "size": 4823040,
    "url": "https://www.youtube.com/watch?v=..."
  }
]
```

---

### DELETE /api/history

Limpia todo el historial.

**Response (200):**
```json
{ "ok": true }
```

---

### DELETE /api/history/{index}

Elimina una entrada del historial por índice.

**Response (200):**
```json
{ "ok": true }
```

**Error (400):**
```json
{ "error": "Indice invalido" }
```

---

### GET /api/config

Obtiene la configuración actual.

**Response (200):**
```json
{
  "default_quality": "192",
  "default_format": "mp3",
  "default_output_dir": "~/Music",
  "non_music_output_dir": "~/Downloads/TubeToAlbum",
  "embed_thumbnail": true,
  "embed_metadata": true,
  "metadata": {
    "clean_title": true
  }
}
```

---

### POST /api/config

Guarda la configuración.

**Request:**
```json
{
  "default_quality": "320",
  "default_format": "mp3",
  "default_output_dir": "~/Music",
  "non_music_output_dir": "~/Downloads/TubeToAlbum",
  "embed_thumbnail": true,
  "embed_metadata": true,
  "metadata": {
    "clean_title": true
  }
}
```

**Response (200):**
```json
{ "ok": true }
```

---

## Gestión de Jobs

Las descargas se ejecutan en `threading.Thread` como daemon. Cada job almacena:

```python
jobs[job_id] = {
    'status': 'downloading',    # downloading|completed|error|cancelled
    'progress': 0.0,            # 0-100
    'speed': '',                # "1.2MB/s"
    'eta': '',                  # "00:12"
    'filepath': '',             # ruta del archivo final
    'error': '',                # mensaje de error si falla
}
```

El frontend hace polling cada 500ms a `/api/progress/{job_id}` para actualizar la barra de progreso.

## Persistencia

- **history.json**: Almacena las últimas 100 descargas
- **config.json**: Configuración del usuario
- Ambos en la raíz del proyecto
