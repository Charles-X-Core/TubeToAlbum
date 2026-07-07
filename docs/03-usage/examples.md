# Ejemplos

## Ejemplo 1: Descargar una Canción

```bash
# Descargar "Bohemian Rhapsody" de Queen
tube2album "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"
```

Resultado:
```
~/Music/Queen/A Night at the Opera/05 - Bohemian Rhapsody.mp3
```

## Ejemplo 2: Descargar con Calidad Máxima

```bash
# Descargar a 320kbps
tube2album "https://www.youtube.com/watch?v=fJ9rUzIMcZQ" -q 320
```

## Ejemplo 3: Descargar Playlist Completa

```bash
# Descargar playlist de "Queen Greatest Hits"
tube2album "https://www.youtube.com/playlist?list=PL..."
```

Resultado:
```
~/Music/Queen/Greatest Hits/
├── 01 - Bohemian Rhapsody.mp3
├── 02 - Another One Bites the Dust.mp3
├── 03 - We Will Rock You.mp3
└── ...
```

## Ejemplo 4: Descargar a Carpeta Personalizada

```bash
# Descargar a carpeta específica
tube2album "https://www.youtube.com/watch?v=..." -o "D:/My Music/Rock"
```

## Ejemplo 5: Descargar Playlist de Álbum

```bash
# Descargar playlist que representa un álbum
tube2album "https://www.youtube.com/playlist?list=PL..." \
  --artist "Queen" \
  --album "A Night at the Opera"
```

## Ejemplo 6: Descargar Solo Audio (sin portada)

```bash
# Sin embeber portada
tube2album "https://www.youtube.com/watch?v=..." --no-thumbnail
```

## Ejemplo 7: Sobrescribir Archivos Existentes

```bash
# Si el archivo ya existe, descargarlo de nuevo
tube2album "https://www.youtube.com/watch?v=..." --overwrite
```

## Ejemplo 8: Modo Detallado

```bash
# Ver información detallada del proceso
tube2album "https://www.youtube.com/watch?v=..." -v
```

## Ejemplo 9: Usar Configuración Personalizada

```bash
# Usar archivo de configuración específico
tube2album "https://www.youtube.com/watch?v=..." --config mi_config.json
```

## Ejemplo 10: Descargar Múltiples URLs

```bash
# Desde archivo de texto
tube2album --batch urls.txt

# Contenido de urls.txt:
# https://youtube.com/watch?v=abc123
# https://youtube.com/watch?v=def456
# https://youtube.com/watch?v=ghi789
```
