import pytest
import os
import tempfile
import shutil
from core.organizer import FileOrganizer


class TestFileOrganizer:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'output_template': '%(artist|uploader)s/%(album|playlist)s/%(title)s.%(ext)s',
            'default_output_dir': self.temp_dir,
            'non_music_output_dir': os.path.join(self.temp_dir, 'non_music'),
            'non_music_video_subdir': 'Videos',
            'non_music_template': '%(uploader)s/%(title)s.%(ext)s',
            'overwrite_existing': False,
        }

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init(self):
        organizer = FileOrganizer(self.config)
        assert organizer.output_dir == self.temp_dir

    def test_sanitize_filename(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_filename('Test: File Name') == 'Test File Name'
        assert organizer.sanitize_filename('Test/File\\Name') == 'TestFileName'
        assert organizer.sanitize_filename('  Test  File  ') == 'Test File'

    def test_sanitize_comma_artist(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_filename('Michael Jackson, Paul McCartney') == 'Michael Jackson'

    def test_sanitize_list_artist(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_filename(['Michael Jackson', 'Paul McCartney']) == 'Michael Jackson'

    def test_sanitize_empty(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_filename('') == ''
        assert organizer.sanitize_filename(None) == ''

    def test_sanitize_artist_feat(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_artist('MYTH & ROID feat. TK (凛として時雨)') == 'MYTH & ROID'

    def test_sanitize_artist_ft(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_artist('Eve ft. Takayan') == 'Eve'

    def test_sanitize_artist_featuring(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_artist('Artist One featuring Artist Two') == 'Artist One'

    def test_sanitize_artist_plain(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_artist('Konomi Suzuki') == 'Konomi Suzuki'

    def test_sanitize_artist_empty(self):
        organizer = FileOrganizer(self.config)
        assert organizer.sanitize_artist('') == ''
        assert organizer.sanitize_artist(None) == ''

    def test_generate_music_filename(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'title': 'Bohemian Rhapsody',
            'ext': 'mp3',
        }
        filename = organizer.generate_music_filename(metadata)
        assert 'Queen' in filename
        assert 'A Night at the Opera' in filename
        assert 'Bohemian Rhapsody.mp3' in filename

    def test_generate_music_filename_defaults(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'title': 'Unknown Title',
        }
        filename = organizer.generate_music_filename(metadata)
        assert 'Unknown Artist' in filename
        assert 'Unknown Album' in filename

    def test_generate_video_filename(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'uploader': 'SomeChannel',
            'title': 'Tutorial Video',
            'ext': 'mp4',
        }
        filename = organizer.generate_video_filename(metadata)
        assert 'SomeChannel' in filename
        assert 'Tutorial Video.mp4' in filename

    def test_get_music_path(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'title': 'Bohemian Rhapsody',
            'ext': 'mp3',
        }
        path = organizer.get_music_path(metadata)
        assert path.startswith(self.temp_dir)
        assert 'Queen' in path
        assert 'A Night at the Opera' in path

    def test_get_video_path(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'uploader': 'SomeChannel',
            'title': 'Tutorial Video',
            'ext': 'mp4',
        }
        path = organizer.get_video_path(metadata)
        assert 'Videos' in path
        assert 'SomeChannel' in path
        assert 'Tutorial Video.mp4' in path

    def test_create_directories(self):
        organizer = FileOrganizer(self.config)
        test_path = os.path.join(self.temp_dir, 'Artist', 'Album', 'song.mp3')
        organizer.create_directories(test_path)
        assert os.path.exists(os.path.join(self.temp_dir, 'Artist', 'Album'))

    def test_organize_music_file(self):
        organizer = FileOrganizer(self.config)
        source_file = os.path.join(self.temp_dir, 'temp.mp3')
        with open(source_file, 'w') as f:
            f.write('test')

        metadata = {
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'title': 'Bohemian Rhapsody',
            'ext': 'mp3',
        }

        dest_path = organizer.organize_music_file(source_file, metadata)
        assert os.path.exists(dest_path)
        assert not os.path.exists(source_file)

    def test_organize_video_file(self):
        organizer = FileOrganizer(self.config)
        source_file = os.path.join(self.temp_dir, 'temp.mp4')
        with open(source_file, 'w') as f:
            f.write('test')

        metadata = {
            'uploader': 'SomeChannel',
            'title': 'Tutorial Video',
            'ext': 'mp4',
        }

        dest_path = organizer.organize_video_file(source_file, metadata)
        assert os.path.exists(dest_path)
        assert not os.path.exists(source_file)

    def test_duplicate_music_handling(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'title': 'Bohemian Rhapsody',
            'ext': 'mp3',
        }

        dest1 = organizer.get_music_path(metadata)
        organizer.create_directories(dest1)
        with open(dest1, 'w') as f:
            f.write('test1')

        source2 = os.path.join(self.temp_dir, 'temp2.mp3')
        with open(source2, 'w') as f:
            f.write('test2')

        dest2 = organizer.organize_music_file(source2, metadata)
        assert os.path.exists(dest2)
        assert '(1)' in dest2

    def test_duplicate_video_handling(self):
        organizer = FileOrganizer(self.config)
        metadata = {
            'uploader': 'SomeChannel',
            'title': 'Tutorial Video',
            'ext': 'mp4',
        }

        dest1 = organizer.get_video_path(metadata)
        organizer.create_directories(dest1)
        with open(dest1, 'w') as f:
            f.write('test1')

        source2 = os.path.join(self.temp_dir, 'temp2.mp4')
        with open(source2, 'w') as f:
            f.write('test2')

        dest2 = organizer.organize_video_file(source2, metadata)
        assert os.path.exists(dest2)
        assert '(1)' in dest2

    def test_organize_file_dispatch_music(self):
        organizer = FileOrganizer(self.config)
        source_file = os.path.join(self.temp_dir, 'temp.mp3')
        with open(source_file, 'w') as f:
            f.write('test')

        metadata = {
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'title': 'Bohemian Rhapsody',
            'ext': 'mp3',
        }

        dest_path = organizer.organize_file(source_file, metadata, is_music=True)
        assert os.path.exists(dest_path)
        assert 'Music' not in dest_path or 'Queen' in dest_path

    def test_organize_file_dispatch_video(self):
        organizer = FileOrganizer(self.config)
        source_file = os.path.join(self.temp_dir, 'temp.mp4')
        with open(source_file, 'w') as f:
            f.write('test')

        metadata = {
            'uploader': 'SomeChannel',
            'title': 'Tutorial Video',
            'ext': 'mp4',
        }

        dest_path = organizer.organize_file(source_file, metadata, is_music=False)
        assert os.path.exists(dest_path)
        assert 'Videos' in dest_path

    def test_get_existing_files(self):
        organizer = FileOrganizer(self.config)
        test_file = os.path.join(self.temp_dir, 'test.mp3')
        with open(test_file, 'w') as f:
            f.write('test')

        existing = organizer.get_existing_files()
        assert test_file in existing
