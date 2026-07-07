import pytest
from core.downloader import TubeToAlbumDownloader


class TestTubeToAlbumDownloader:
    def setup_method(self):
        self.config = {
            'format': 'mp3',
            'quality': '192',
            'output': {
                'output_template': '%(artist|uploader)s/%(album|playlist)s/%(track_number)02d - %(title)s.%(ext)s',
            },
            'quiet': True,
        }

    def test_init(self):
        downloader = TubeToAlbumDownloader(self.config)
        assert downloader.config == self.config
        assert downloader.ydl_opts is not None

    def test_build_options_format(self):
        downloader = TubeToAlbumDownloader(self.config)
        postprocessors = downloader.ydl_opts['postprocessors']
        ffmpeg_postprocessor = [pp for pp in postprocessors if pp['key'] == 'FFmpegExtractAudio'][0]
        assert ffmpeg_postprocessor['preferredcodec'] == 'mp3'
        assert ffmpeg_postprocessor['preferredquality'] == '192'

    def test_build_options_template(self):
        downloader = TubeToAlbumDownloader(self.config)
        template = downloader.ydl_opts['outtmpl']
        assert '%(title)s' in template

    def test_build_options_writethumbnail(self):
        downloader = TubeToAlbumDownloader(self.config)
        assert downloader.ydl_opts['writethumbnail'] is True

    def test_build_options_quiet(self):
        downloader = TubeToAlbumDownloader(self.config)
        assert downloader.ydl_opts['quiet'] is True

    def test_parse_info(self):
        downloader = TubeToAlbumDownloader(self.config)
        info = {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'thumbnail': 'https://img.youtube.com/vi/fJ9rUzIMcZQ/maxresdefault.jpg',
            'duration': 354,
            'upload_date': '19751031',
            'track_number': 5,
            'description': 'Official video',
        }
        parsed = downloader._parse_info(info)
        assert parsed['title'] == 'Bohemian Rhapsody'
        assert parsed['artist'] == 'Queen'
        assert parsed['album'] == 'A Night at the Opera'
        assert parsed['duration'] == 354
        assert parsed['track_number'] == 5

    def test_parse_info_fallback_uploader(self):
        downloader = TubeToAlbumDownloader(self.config)
        info = {
            'title': 'Some Video',
            'uploader': 'Some Channel',
            'album': None,
            'playlist': 'My Playlist',
        }
        parsed = downloader._parse_info(info)
        assert parsed['artist'] == 'Some Channel'
        assert parsed['album'] == 'My Playlist'

    def test_parse_info_missing_fields(self):
        downloader = TubeToAlbumDownloader(self.config)
        info = {}
        parsed = downloader._parse_info(info)
        assert parsed['title'] is None
        assert parsed['artist'] is None
        assert parsed['album'] is None
