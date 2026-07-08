import argparse
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.downloader import TubeToAlbumDownloader
from core.video_downloader import VideoDownloader
from core.parser import TitleParser
from core.thumbnail import ThumbnailHandler
from core.organizer import FileOrganizer
from core.content_detector import ContentDetector
from utils.config_utils import load_config, get_config_value
from utils.url_utils import is_youtube_url, is_youtube_playlist, extract_video_id


def print_analysis(analysis: dict, info: dict):
    print("\n" + "=" * 50)
    print("  ANÁLISIS DE CONTENIDO")
    print("=" * 50)

    if analysis['is_music']:
        print("  Tipo: MÚSICA")
    else:
        print("  Tipo: OTRO CONTENIDO")

    confidence_map = {'high': 'Alta', 'medium': 'Media', 'low': 'Baja'}
    print(f"  Confianza: {confidence_map.get(analysis['confidence'], analysis['confidence'])}")

    if analysis['suggested_artist']:
        print(f"  Artista: {analysis['suggested_artist']}")
    if analysis['suggested_album']:
        print(f"  Álbum: {analysis['suggested_album']}")

    print(f"  Título: {info.get('title', 'N/A')}")
    print(f"  Canal: {info.get('artist', 'N/A')}")

    print("\n  Razón:")
    for reason in analysis['reasons']:
        print(f"    • {reason}")
    print("=" * 50)


def ask_user_confirmation(analysis: dict) -> bool:
    if analysis['is_music']:
        response = input("\n¿Es correcto? [S/n]: ").strip().lower()
        return response != 'n'
    else:
        return True


def ask_format_and_quality(is_music: bool) -> tuple:
    if is_music:
        print("\n¿Qué formato deseas?")
        print("  [1] MP3 - Estándar (128 kbps)")
        print("  [2] MP3 - Alta calidad (192 kbps) - Recomendado")
        print("  [3] MP3 - Muy alta (256 kbps)")
        print("  [4] MP3 - Máxima (320 kbps)")
        print("  [5] M4A - Calidad nativa YouTube (mejor fidelidad)")

        while True:
            choice = input("\nSelección [2]: ").strip() or '2'
            if choice == '1':
                return 'mp3', '128'
            elif choice == '2':
                return 'mp3', '192'
            elif choice == '3':
                return 'mp3', '256'
            elif choice == '4':
                return 'mp3', '320'
            elif choice == '5':
                return 'm4a', '256'
            print("Opción no válida.")
    else:
        print("\n¿Qué formato deseas?")
        print("  [1] MP4 - Video 360p (ligero)")
        print("  [2] MP4 - Video 480p")
        print("  [3] MP4 - Video 720p (HD) - Recomendado")
        print("  [4] MP4 - Video 1080p (Full HD)")
        print("  [5] MP4 - Mejor calidad disponible")
        print("  [6] MP3 - Solo audio (128 kbps)")
        print("  [7] MP3 - Solo audio (192 kbps)")
        print("  [8] MP3 - Solo audio (256 kbps)")
        print("  [9] MP3 - Solo audio (320 kbps)")

        while True:
            choice = input("\nSelección [3]: ").strip() or '3'
            if choice == '1':
                return 'mp4', '360'
            elif choice == '2':
                return 'mp4', '480'
            elif choice == '3':
                return 'mp4', '720'
            elif choice == '4':
                return 'mp4', '1080'
            elif choice == '5':
                return 'mp4', 'best'
            elif choice == '6':
                return 'mp3', '128'
            elif choice == '7':
                return 'mp3', '192'
            elif choice == '8':
                return 'mp3', '256'
            elif choice == '9':
                return 'mp3', '320'
            print("Opción no válida.")


def ask_destination(is_music: bool, format_choice: str) -> str:
    if is_music:
        return 'music'

    print("\n¿Dónde quieres guardar?")
    print("  [1] C:\\Downloads\\TubeToAlbum\\ (carpeta por defecto)")
    print("  [2] Elegir ubicación personalizada")

    while True:
        choice = input("\nSelección [1]: ").strip() or '1'
        if choice == '1':
            return 'default'
        elif choice == '2':
            custom_path = input("Ruta completa: ").strip()
            if custom_path:
                return custom_path
            print("Ruta no válida.")
        print("Opción no válida.")


def ask_more_options() -> dict:
    options = {'embed_metadata': True, 'embed_thumbnail': True}

    print("\n¿Opciones adicionales?")
    print("  [S/n] ¿Embeber portada del video? (S/n): ", end='')
    thumb = input().strip().lower()
    if thumb == 'n':
        options['embed_thumbnail'] = False

    print("  [S/n] ¿Embeber metadata (artista, título, etc.)? (S/n): ", end='')
    meta = input().strip().lower()
    if meta == 'n':
        options['embed_metadata'] = False

    return options


def main():
    parser = argparse.ArgumentParser(
        description='TubeToAlbum - Descargador profesional de YouTube a MP3/MP4',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  tube2album https://www.youtube.com/watch?v=VIDEO_ID
  tube2album https://www.youtube.com/watch?v=VIDEO_ID --quality 320
  tube2album https://www.youtube.com/playlist?list=PLAYLIST_ID
  tube2album --info https://www.youtube.com/watch?v=VIDEO_ID
  tube2album https://www.youtube.com/watch?v=VIDEO_ID --format mp4
  tube2album https://www.youtube.com/watch?v=VIDEO_ID --no-interactive
        """
    )

    parser.add_argument('url', nargs='?', help='URL del video o playlist de YouTube')
    parser.add_argument('--info', action='store_true', help='Mostrar información sin descargar')
    parser.add_argument('--quality', '-q', choices=['128', '192', '256', '320', '360', '480', '720', '1080', 'best'],
                        help='Calidad del audio/video')
    parser.add_argument('--format', '-f', choices=['mp3', 'm4a', 'mp4'],
                        help='Formato del audio/video')
    parser.add_argument('--output', '-o', help='Directorio de salida')
    parser.add_argument('--config', '-c', help='Ruta al archivo de configuración')
    parser.add_argument('--verbose', '-v', action='store_true', help='Modo verbose')
    parser.add_argument('--yes', '-y', action='store_true', help='Aceptar todas las preguntas (calidad por defecto)')
    parser.add_argument('--no-interactive', action='store_true', help='Sin preguntas, usar configuración por defecto')
    parser.add_argument('--mp4', action='store_true', help='Descargar como MP4 (atajo)')
    parser.add_argument('--mp3', action='store_true', help='Descargar como MP3 (atajo)')

    args = parser.parse_args()

    if not args.url:
        parser.print_help()
        sys.exit(1)

    if not is_youtube_url(args.url):
        print("Error: URL de YouTube no válida")
        sys.exit(1)

    config = load_config(args.config)

    if args.quality:
        config['default_quality'] = args.quality
    if args.format:
        config['default_format'] = args.format
    if args.output:
        config['default_output_dir'] = args.output

    if args.verbose:
        print(f"Configuración: {json.dumps(config, indent=2)}")

    downloader_config = {
        'format': config.get('default_format', 'mp3'),
        'quality': config.get('default_quality', '320'),
        'output': {
            'output_template': config.get('output_template'),
            'output_dir': config.get('default_output_dir'),
        },
        'default_output_dir': config.get('default_output_dir', '~/Music'),
        'output_template': config.get('output_template'),
        'non_music_output_dir': config.get('non_music_output_dir', '~/Downloads/TubeToAlbum'),
        'quiet': not args.verbose,
    }

    video_downloader_config = {
        'non_music_output_dir': config.get('non_music_output_dir', '~/Downloads/TubeToAlbum'),
        'non_music_video_subdir': config.get('non_music_video_subdir', 'Videos'),
        'quiet': not args.verbose,
    }

    downloader = TubeToAlbumDownloader(downloader_config)
    vid_downloader = VideoDownloader(video_downloader_config)
    parser_engine = TitleParser(config)
    thumbnail_handler = ThumbnailHandler()
    organizer = FileOrganizer(config)
    detector = ContentDetector()

    try:
        print(f"Obteniendo información de: {args.url}")
        info = downloader.get_info(args.url)

        if args.info:
            print("\n=== Información del Video ===")
            print(f"Título: {info['title']}")
            print(f"Artista: {info['artist']}")
            print(f"Álbum: {info['album']}")
            print(f"Duración: {info['duration']} segundos")
            sys.exit(0)

        analysis = detector.detect(info)
        print_analysis(analysis, info)

        is_playlist = is_youtube_playlist(args.url)

        if is_playlist:
            print("\nDetectada playlist - descargando...")
            downloader.download_playlist(args.url)
            print("\n¡Proceso completado!")
            sys.exit(0)

        if not args.yes:
            if not ask_user_confirmation(analysis):
                print("Descarga cancelada por el usuario.")
                sys.exit(0)

        if args.mp4:
            format_choice = 'mp4'
            quality = args.quality or '720'
        elif args.mp3:
            format_choice = 'mp3'
            quality = args.quality or '192'
        elif args.format and args.quality:
            format_choice = args.format
            quality = args.quality
        elif args.no_interactive:
            format_choice = config.get('default_format', 'mp3')
            quality = config.get('default_quality', '320')
        else:
            format_choice, quality = ask_format_and_quality(analysis['is_music'])

        if format_choice == 'mp4':
            vid_quality = quality if quality in ['360', '480', '720', '1080', 'best'] else '720'
            video_downloader_config['video_quality'] = vid_quality
            vid_downloader = VideoDownloader(video_downloader_config)

            print(f"\nDescargando VIDEO ({vid_quality}p): {info['title']}")

            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%')
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    print(f"\r{percent} | Speed: {speed} | ETA: {eta}", end='')
                elif d['status'] == 'finished':
                    print("\n¡Descarga completada!")

            vid_downloader.download(args.url, progress_callback=progress_hook)

            dest_dir = os.path.expanduser(
                config.get('non_music_output_dir', '~/Downloads/TubeToAlbum'))
            print(f"\nGuardado en: {dest_dir}/")

        else:
            parsed = parser_engine.parse_youtube_title(info['title'], info['artist'])
            metadata = {
                'title': parsed['title'],
                'artist': parsed['artist'],
                'album': info['album'] or config.get('metadata', {}).get('default_album', 'Unknown Album'),
                'track_number': info['track_number'] or 0,
                'ext': format_choice if format_choice != 'm4a' else 'm4a',
            }

            print(f"\nDescargando: {metadata['title']}")
            print(f"Artista: {metadata['artist']}")
            print(f"Álbum: {metadata['album']}")
            print(f"Formato: {format_choice.upper()} {quality} kbps")

            downloader_config['format'] = format_choice if format_choice != 'm4a' else 'm4a'
            downloader_config['quality'] = quality
            downloader = TubeToAlbumDownloader(downloader_config)

            def progress_hook(d):
                if d['status'] == 'downloading':
                    percent = d.get('_percent_str', '0%')
                    speed = d.get('_speed_str', 'N/A')
                    eta = d.get('_eta_str', 'N/A')
                    print(f"\r{percent} | Speed: {speed} | ETA: {eta}", end='')
                elif d['status'] == 'finished':
                    print("\n¡Descarga completada!")

            is_music = analysis['is_music']
            dest_path = downloader.download(args.url, progress_callback=progress_hook, is_music=is_music)

            if dest_path:
                print(f"\nGuardado en: {dest_path}")
            else:
                dest_dir = os.path.expanduser(config.get('default_output_dir', '~/Music'))
                print(f"\nGuardado en: {dest_dir}/")

        print("\n¡Proceso completado!")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
