# Uso GUI (Electron)

## Iniciar la Aplicación

```bash
# Opción 1: Script automático (Windows)
start.bat

# Opción 2: Manual
cd backend && python server.py    # Terminal 1
cd electron && npm start          # Terminal 2
```

## Estructura de la Interfaz

```
┌──────────────────────────────────────────────────────────────┐
│  [icono] TubeToAlbum                        [─] [□] [X]    │
├──────────┬───────────────────────────────────────────────────┤
│          │                                                   │
│ ● Online │  Descargar                                        │
│          │  Pega un enlace de YouTube y descálgalo al instante
│ ┌──────┐ │                                                   │
│ │Descar│ │  ┌─────────────────────────────────────────────┐  │
│ │gar   │ │  │ 🔗 URL de YouTube                           │  │
│ └──────┘ │  │ ┌─────────────────────────────────────┐     │  │
│ ┌──────┐ │  │ │ https://youtube.com/watch?v=...     │     │  │
│ │Histo-│ │  │ └─────────────────────────────────────┘     │  │
│ │rial  │ │  │                          [🔍 Obtener Info]  │  │
│ └──────┘ │  └─────────────────────────────────────────────┘  │
│ ┌──────┐ │                                                   │
│ │Confi-│ │  ┌─────────────────────────────────────────────┐  │
│ │gurar │ │  │  [thumbnail]  Bohemian Rhapsody             │  │
│ └──────┘ │  │               Canal: Queen                   │  │
│          │  │               [MUSICA]  5:54                 │  │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                   │
│ v1.0.0   │  ┌─────────────────────────────────────────────┐  │
│          │  │ Opciones de descarga                         │  │
│          │  │ Formato: [MP3 ▼]  Calidad: [192 kbps ▼]    │  │
│          │  │ Guardar en: [C:\Music] [📁]                  │  │
│          │  │ [🎵 Mi Música] [⬇ Descargas] [📁 Escritorio]│  │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                   │
│          │  ┌─────────────────────────────────────────────┐  │
│          │  │ Descargando... 65.3%                        │  │
│          │  │ ████████████████░░░░░░░░  1.2 MB/s  ETA: 12s│  │
│          │  └─────────────────────────────────────────────┘  │
│          │                                                   │
│          │              [⬇ Descargar]  [✕ Cancelar]         │
│          │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

## Tabs

### Tab Descargar
1. **Input de URL**: Pegar enlace de YouTube o YouTube Music
2. **Obtener Info**: Botón que analiza el video
3. **Preview**: Muestra título, artista, thumbnail, duración, tipo (música/otro)
4. **Opciones**: Formato (MP3/M4A/MP4), calidad, carpeta de destino
5. **Quick Paths**: Botones rápidos para Mi Música, Descargas, Escritorio, Personalizar
6. **Progreso**: Barra de progreso con velocidad y ETA
7. **Acciones**: Botón Descargar / Cancelar

### Tab Historial
- Tabla con: Título, Artista, Formato, Tamaño, Fecha, Acción
- Botón "Limpiar todo" con modal de confirmación
- Botón "Eliminar" por cada entrada

### Tab Configuración
- **Valores por defecto**: Calidad y formato
- **Carpetas de destino**: Música y Otros contenidos
- **Metadata**: Toggle switches para portada, metadata, limpiar títulos
- **Acciones**: Guardar / Restablecer por defecto

## Controles de Ventana
- **Minimizar (─)**: Minimiza la ventana
- **Maximizar (□)**: Maximiza o restaura la ventana
- **Cerrar (X)**: Cierra la aplicación (fondo rojo en hover)

## Funcionalidades

### Preview antes de Descargar
1. Pegar URL de YouTube
2. Hacer clic en "Obtener Info"
3. Ver título, artista, portada, duración
4. Ver tipo de contenido (Música / Otro Contenido)
5. Seleccionar formato y calidad
6. Hacer clic en "Descargar"

### Detección de Contenido
- Análisis automático del video
- Badge verde "MUSICA" o rojo "OTRO CONTENIDO"
- Razones del análisis mostradas debajo
- Para contenido no-música: se sugiere formato MP4

### Folder Picker
- Botón 🩹 para abrir diálogo nativo del sistema
- Quick paths para carpetas comunes
- Ruta visible en el input

### Historial
- Todas las descargas se guardan automáticamente
- Máximo 100 entradas
- Se muestra tamaño del archivo en formato legible

### Configuración
- Calidad por defecto: 128, 192, 256, 320 kbps
- Formato por defecto: MP3, M4A, MP4
- Carpetas de destino personalizables
- Opciones de metadata con toggle switches
