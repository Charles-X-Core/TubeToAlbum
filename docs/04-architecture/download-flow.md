# Flujo de Descarga

## Flujo Completo

```
┌─────────────────────────────────────────────────────────┐
│ 1. ENTRADA                                              │
│    Usuario proporciona URL de YouTube                    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 2. EXTRACCIÓN DE INFORMACIÓN                            │
│    yt-dlp.extract_info(url, download=False)              │
│    → Obtiene: título, artista, álbum, thumbnail, etc.   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 3. PARSEO DE METADATA                                   │
│    parser.parse_youtube_title(title, uploader)           │
│    → Limpia título, extrae artista                      │
│    → Valida contra playlists si existen                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 4. PREVIEW (opcional)                                   │
│    Muestra al usuario:                                  │
│    - Título limpio                                      │
│    - Artista detectado                                  │
│    - Portada del video                                  │
│    - Permite editar antes de descargar                  │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 5. DESCARGA DE AUDIO                                    │
│    yt-dlp.download([url])                               │
│    → Descarga mejor calidad de audio disponible         │
│    → Formato original: M4A (AAC) o WebM (Opus)         │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 6. CONVERSIÓN DE AUDIO                                  │
│    FFmpegExtraAudio postprocessor                       │
│    → Convierte a MP3 con calidad especificada           │
│    → Ejemplo: M4A 256kbps → MP3 192kbps                │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 7. EMBEBED DE METADATA                                  │
│    Mutagen escribe tags ID3 en el MP3:                  │
│    - TIT2 (título)                                      │
│    - TPE1 (artista)                                     │
│    - TALB (álbum)                                       │
│    - TRCK (número de pista)                             │
│    - TDRC (año)                                         │
│    - TCON (género)                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 8. EMBEBED DE PORTADA                                   │
│    Mutagen escribe frame APIC:                          │
│    - Descarga thumbnail de YouTube                      │
│    - Convierte a JPEG si es necesario                   │
│    - Embebe en el MP3                                   │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 9. ORGANIZACIÓN DE ARCHIVOS                             │
│    organizer.organize_file()                            │
│    - Crea carpetas: Artista/Álbum/                      │
│    - Renombra archivo: 01 - Título.mp3                  │
│    - Mueve a ubicación final                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│ 10. COMPLETADO                                          │
│    - Archivo guardado en ubicación final                │
│    - Metadata completa embebida                         │
│    - Portada visible en reproductores                   │
│    - Listo para reproducir                              │
└─────────────────────────────────────────────────────────┘
```

## Flujo para Playlist

```
URL de Playlist
    │
    ▼
Extraer info de playlist
    │
    ▼
Para CADA video en la playlist:
    │
    ├──→ Extraer info del video
    ├──→ Parsear metadata
    ├──→ Descargar audio
    ├──→ Convertir a MP3
    ├──→ Embeber metadata
    ├──→ Embeber portada
    └──→ Organizar en carpeta
    │
    ▼
Playlist completa descargada
```

## Manejo de Errores

```
Error durante descarga
    │
    ├──→ Error de red → Reintentar (máx 3 veces)
    ├──→ Video no disponible → Saltar, registrar error
    ├──→ Calidad no disponible → Usar siguiente calidad
    ├──→ FFmpeg error → Registrar, continuar
    └──→ Error desconocido → Registrar, continuar
    
Al final:
    → Resumen: X descargadas, Y fallidas
    → Lista de errores para revisión
```
