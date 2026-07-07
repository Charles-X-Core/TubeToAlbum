import pytest
from core.content_detector import ContentDetector


class TestContentDetector:
    def setup_method(self):
        self.detector = ContentDetector()

    def test_detect_music_with_artist_album(self):
        info = {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'uploader': 'Queen Official',
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True
        assert result['confidence'] == 'high'

    def test_detect_music_with_official_video(self):
        info = {
            'title': 'Bohemian Rhapsody (Official Video)',
            'artist': None,
            'album': None,
            'uploader': 'Queen Official',
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_detect_music_with_playlist(self):
        info = {
            'title': 'Some Song',
            'artist': None,
            'album': None,
            'playlist': 'Best Rock Songs',
            'uploader': 'Music Channel',
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_detect_music_short_duration(self):
        info = {
            'title': 'My Song',
            'artist': None,
            'album': None,
            'uploader': 'Artist',
            'duration': 210,
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_detect_non_music_tutorial(self):
        info = {
            'title': 'Python Tutorial for Beginners',
            'artist': None,
            'album': None,
            'uploader': 'Code Academy',
            'duration': 1800,
        }
        result = self.detector.detect(info)
        assert result['is_music'] is False

    def test_detect_non_music_podcast(self):
        info = {
            'title': 'Podcast Episode 45 - Interview with Expert',
            'artist': None,
            'album': None,
            'uploader': 'Podcast Channel',
            'duration': 3600,
        }
        result = self.detector.detect(info)
        assert result['is_music'] is False

    def test_detect_non_music_vlog(self):
        info = {
            'title': 'Daily Vlog - My Life in Japan',
            'artist': None,
            'album': None,
            'uploader': 'Vlogger',
            'duration': 900,
        }
        result = self.detector.detect(info)
        assert result['is_music'] is False

    def test_detect_music_category(self):
        info = {
            'title': 'Some Video',
            'artist': None,
            'album': None,
            'uploader': 'Channel',
            'categories': ['Music'],
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_detect_low_confidence(self):
        info = {
            'title': 'Random Video',
            'artist': None,
            'album': None,
            'uploader': 'Random Channel',
        }
        result = self.detector.detect(info)
        assert result['confidence'] == 'low'

    def test_detect_medium_confidence(self):
        info = {
            'title': 'Song Cover',
            'artist': None,
            'album': None,
            'uploader': 'Cover Artist',
        }
        result = self.detector.detect(info)
        assert result['confidence'] == 'medium'

    def test_suggested_artist_from_info(self):
        info = {
            'title': 'Some Song',
            'artist': 'Known Artist',
            'album': None,
            'uploader': 'Some Channel',
        }
        result = self.detector.detect(info)
        assert result['suggested_artist'] == 'Known Artist'

    def test_suggested_artist_fallback_to_uploader(self):
        info = {
            'title': 'Some Song',
            'artist': None,
            'album': None,
            'uploader': 'Some Channel',
        }
        result = self.detector.detect(info)
        assert result['suggested_artist'] == 'Some Channel'

    def test_detect_music_lyrics(self):
        info = {
            'title': 'Song Name (Lyrics)',
            'artist': None,
            'album': None,
            'uploader': 'Lyrics Channel',
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_detect_music_audio(self):
        info = {
            'title': 'Song Name (Official Audio)',
            'artist': None,
            'album': None,
            'uploader': 'Artist',
        }
        result = self.detector.detect(info)
        assert result['is_music'] is True

    def test_reasons_provided(self):
        info = {
            'title': 'Song',
            'artist': 'Artist',
            'album': 'Album',
            'uploader': 'Channel',
        }
        result = self.detector.detect(info)
        assert len(result['reasons']) > 0
