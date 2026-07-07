import pytest
from core.parser import TitleParser


class TestTitleParser:
    def setup_method(self):
        self.parser = TitleParser()

    def test_parse_artist_title_separator(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody')
        assert result['artist'] == 'Queen'
        assert result['title'] == 'Bohemian Rhapsody'

    def test_parse_artist_title_dash(self):
        result = self.parser.parse_youtube_title('Led Zeppelin - Stairway to Heaven')
        assert result['artist'] == 'Led Zeppelin'
        assert result['title'] == 'Stairway to Heaven'

    def test_parse_artist_title_pipe(self):
        result = self.parser.parse_youtube_title('Pink Floyd | Comfortably Numb')
        assert result['artist'] == 'Pink Floyd'
        assert result['title'] == 'Comfortably Numb'

    def test_parse_artist_title_colon(self):
        result = self.parser.parse_youtube_title('AC/DC: Thunderstruck')
        assert result['artist'] == 'AC/DC'
        assert result['title'] == 'Thunderstruck'

    def test_clean_official_video(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody (Official Video)')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_clean_official_music_video(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody [Official Music Video]')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_clean_hd(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody [HD]')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_clean_4k(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody [4K]')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_clean_lyrics(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody (Lyrics)')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_fallback_to_uploader(self):
        result = self.parser.parse_youtube_title('Some Random Title', uploader='Queen Official')
        assert result['artist'] == 'Queen Official'

    def test_fallback_to_default_artist(self):
        result = self.parser.parse_youtube_title('Some Random Title')
        assert result['artist'] == 'Unknown Artist'

    def test_parse_playlist_title(self):
        result = self.parser.parse_playlist_title('Queen - A Night at the Opera')
        assert result['artist'] == 'Queen'
        assert result['album'] == 'A Night at the Opera'

    def test_parse_upload_date(self):
        result = self.parser.parse_upload_date('19751031')
        assert result == '1975-10-31'

    def test_parse_upload_date_invalid(self):
        result = self.parser.parse_upload_date('invalid')
        assert result is None

    def test_parse_upload_date_none(self):
        result = self.parser.parse_upload_date(None)
        assert result is None

    def test_multiple_cleanups(self):
        result = self.parser.parse_youtube_title('Queen - Bohemian Rhapsody (Official Video) [HD]')
        assert result['title'] == 'Bohemian Rhapsody'

    def test_feat_in_title(self):
        result = self.parser.parse_youtube_title('Artist A - Song (feat. Artist B)')
        assert result['artist'] == 'Artist A'
        assert 'feat. Artist B' in result['title']

    def test_ft_in_title(self):
        result = self.parser.parse_youtube_title('Artist A - Song ft. Artist B')
        assert result['artist'] == 'Artist A'
        assert 'ft. Artist B' in result['title']
