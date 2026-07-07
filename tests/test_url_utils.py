import pytest
from utils.url_utils import (
    is_youtube_url, is_youtube_playlist,
    extract_video_id, extract_playlist_id, clean_youtube_url,
    sanitize_youtube_url
)


class TestUrlUtils:
    def test_is_youtube_url_standard(self):
        assert is_youtube_url('https://www.youtube.com/watch?v=fJ9rUzIMcZQ') is True

    def test_is_youtube_url_short(self):
        assert is_youtube_url('https://youtu.be/fJ9rUzIMcZQ') is True

    def test_is_youtube_url_embed(self):
        assert is_youtube_url('https://www.youtube.com/embed/fJ9rUzIMcZQ') is True

    def test_is_youtube_url_invalid(self):
        assert is_youtube_url('https://www.example.com/video') is False

    def test_is_youtube_playlist(self):
        assert is_youtube_playlist('https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf') is True

    def test_is_youtube_playlist_with_video(self):
        assert is_youtube_playlist('https://www.youtube.com/watch?v=fJ9rUzIMcZQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf') is False

    def test_is_youtube_playlist_radio(self):
        assert is_youtube_playlist('https://www.youtube.com/watch?v=abc123&list=RDabc123&start_radio=1') is False

    def test_is_youtube_playlist_invalid(self):
        assert is_youtube_playlist('https://www.youtube.com/watch?v=fJ9rUzIMcZQ') is False

    def test_extract_video_id(self):
        assert extract_video_id('https://www.youtube.com/watch?v=fJ9rUzIMcZQ') == 'fJ9rUzIMcZQ'
        assert extract_video_id('https://youtu.be/fJ9rUzIMcZQ') == 'fJ9rUzIMcZQ'
        assert extract_video_id('https://www.youtube.com/embed/fJ9rUzIMcZQ') == 'fJ9rUzIMcZQ'

    def test_extract_video_id_invalid(self):
        assert extract_video_id('https://www.example.com/video') is None

    def test_extract_playlist_id(self):
        assert extract_playlist_id('https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf') == 'PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf'

    def test_extract_playlist_id_invalid(self):
        assert extract_playlist_id('https://www.youtube.com/watch?v=fJ9rUzIMcZQ') is None

    def test_clean_youtube_url(self):
        assert clean_youtube_url('youtube.com/watch?v=fJ9rUzIMcZQ') == 'https://youtube.com/watch?v=fJ9rUzIMcZQ'
        assert clean_youtube_url('https://youtube.com/watch?v=fJ9rUzIMcZQ') == 'https://youtube.com/watch?v=fJ9rUzIMcZQ'
        assert clean_youtube_url('  https://youtube.com/watch?v=fJ9rUzIMcZQ  ') == 'https://youtube.com/watch?v=fJ9rUzIMcZQ'

    def test_sanitize_youtube_url_radio(self):
        url = 'https://www.youtube.com/watch?v=JHDbhtskbuA&list=RDJHDbhtskbuA&start_radio=1'
        assert sanitize_youtube_url(url) == 'https://www.youtube.com/watch?v=JHDbhtskbuA'

    def test_sanitize_youtube_url_normal(self):
        url = 'https://www.youtube.com/watch?v=abc123def45'
        assert sanitize_youtube_url(url) == 'https://www.youtube.com/watch?v=abc123def45'

    def test_sanitize_youtube_url_short(self):
        url = 'https://youtu.be/abc123def45'
        assert sanitize_youtube_url(url) == 'https://youtu.be/abc123def45'
