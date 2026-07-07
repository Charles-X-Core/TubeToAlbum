# Arquitectura Electron

## Visión General

TubeToAlbum usa una arquitectura de dos procesos:
- **Electron (Frontend)**: Interfaz gráfica con HTML/CSS/JS
- **Python (Backend)**: API REST Flask con la lógica de descarga

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                    ELECTRON MAIN PROCESS                        │
│                                                                 │
│  main.js                                                        │
│  ├── Crea BrowserWindow (frameless)                             │
│  ├── Spawn backend Python (child_process)                       │
│  ├── Espera backend en http://127.0.0.1:5000                   │
│  └── Handlers IPC:                                              │
│      ├── window-minimize                                        │
│      ├── window-maximize                                        │
│      ├── window-close                                           │
│      ├── select-folder (abre diálogo nativo)                    │
│      └── open-folder (abre carpeta en explorador)               │
│                                                                 │
│  preload.js                                                     │
│  └── contextBridge → window.api                                 │
│      ├── getInfo(url)                                           │
│      ├── startDownload(data)                                    │
│      ├── getProgress(jobId)                                     │
│      ├── cancelDownload(jobId)                                  │
│      ├── getHistory / clearHistory / deleteHistoryEntry         │
│      ├── getConfig / saveConfig                                 │
│      ├── minimizeWindow / maximizeWindow / closeWindow          │
│      └── selectFolder / openFolder                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ fetch() HTTP
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PYTHON BACKEND                               │
│                                                                 │
│  backend/server.py (Flask)                                      │
│  ├── GET  /api/config                                           │
│  ├── POST /api/config                                           │
│  ├── POST /api/info        → info + analysis                   │
│  ├── POST /api/download    → job_id (threading)                │
│  ├── GET  /api/progress/<id> → status, progress, speed, eta    │
│  ├── POST /api/cancel/<id>                                        │
│  ├── GET  /api/history                                          │
│  ├── DELETE /api/history                                        │
│  └── DELETE /api/history/<index>                                │
│                                                                 │
│  core/ modules                                                  │
│  ├── downloader.py (TubeToAlbumDownloader)                      │
│  ├── video_downloader.py (VideoDownloader)                      │
│  ├── content_detector.py (ContentDetector)                      │
│  ├── metadata.py (MetadataWriter)                               │
│  ├── parser.py (TitleParser)                                    │
│  ├── thumbnail.py (ThumbnailHandler)                            │
│  └── organizer.py (FileOrganizer)                               │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

### 1. Fetch Info
```
Renderer → fetch('/api/info') → Flask → yt-dlp.extract_info()
         ← { info, analysis } ← ContentDetector.detect()
```

### 2. Download
```
Renderer → fetch('/api/download') → Flask → threading.Thread()
         ← { job_id }            → TubeToAlbumDownloader.download()
                                    ↓
         ← poll '/api/progress'  ← progress_hook() actualiza jobs[]
```

### 3. History
```
Download completo → Flask guarda entry en history.json
Renderer → fetch('/api/history') → Flask lee history.json
```

## Seguridad

- **contextBridge**: Aísla el renderer del Node.js directo
- **CORS**: Configurado para localhost:5000
- **No nodeIntegration**: Renderer no tiene acceso a `require()`
- **contextIsolation**: Cada frame tiene su propio contexto

## Proceso de Arranque

1. `start.bat` ejecuta `python backend/server.py`
2. Espera 3 segundos
3. Ejecuta `cd electron && npm start`
4. Electron ejecuta `main.js`
5. `main.js` hace spawn de `server.py` como child process
6. `waitForBackend()` intenta conectarse a `/api/config` cada 500ms
7. Cuando responde, crea el BrowserWindow
8. Carga `renderer/index.html`

## Dependencias

### Electron
- `electron ^28.0.0`

### Python Backend
- `flask >= 3.0.0`
- `flask-cors >= 4.0.0`
- `yt-dlp >= 2026.1.0`
- `mutagen >= 1.47.0`
- `Pillow >= 10.0.0`
