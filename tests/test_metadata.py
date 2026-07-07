import pytest
import os
import tempfile
from core.metadata import MetadataWriter


class TestMetadataWriter:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_mp3 = os.path.join(self.temp_dir, 'test.mp3')
        MetadataWriter.create_test_mp3(self.test_mp3)

    def teardown_method(self):
        if os.path.exists(self.test_mp3):
            os.remove(self.test_mp3)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_init(self):
        writer = MetadataWriter(self.test_mp3)
        assert writer.filepath == self.test_mp3
        assert writer.audio is not None

    def test_write_basic(self):
        writer = MetadataWriter(self.test_mp3)
        writer.write_basic('Bohemian Rhapsody', 'Queen', 'A Night at the Opera')
        writer.save()

        reader = MetadataWriter(self.test_mp3)
        metadata = reader.read()
        assert metadata['title'] == 'Bohemian Rhapsody'
        assert metadata['artist'] == 'Queen'
        assert metadata['album'] == 'A Night at the Opera'

    def test_write_extended(self):
        writer = MetadataWriter(self.test_mp3)
        writer.write_basic('Test', 'Artist', 'Album')
        writer.write_extended(track_number=5, year='1975', genre='Rock')
        writer.save()

        reader = MetadataWriter(self.test_mp3)
        metadata = reader.read()
        assert metadata['track_number'] == '5'
        assert metadata['year'] == '1975'
        assert metadata['genre'] == 'Rock'

    def test_write_thumbnail(self):
        writer = MetadataWriter(self.test_mp3)
        writer.write_basic('Test', 'Artist', 'Album')

        fake_image = b'\xff\xd8\xff\xe0' + b'\x00' * 100
        writer.write_thumbnail(fake_image)
        writer.save()

        reader = MetadataWriter(self.test_mp3)
        assert 'APIC:Cover' in reader.audio.tags

    def test_write_all(self):
        writer = MetadataWriter(self.test_mp3)
        metadata = {
            'title': 'Bohemian Rhapsody',
            'artist': 'Queen',
            'album': 'A Night at the Opera',
            'track_number': 5,
            'year': '1975',
            'genre': 'Rock',
        }
        writer.write_all(metadata)
        writer.save()

        reader = MetadataWriter(self.test_mp3)
        result = reader.read()
        assert result['title'] == 'Bohemian Rhapsody'
        assert result['artist'] == 'Queen'
        assert result['album'] == 'A Night at the Opera'
        assert result['track_number'] == '5'
        assert result['year'] == '1975'
        assert result['genre'] == 'Rock'

    def test_write_all_with_thumbnail(self):
        writer = MetadataWriter(self.test_mp3)
        metadata = {
            'title': 'Test',
            'artist': 'Artist',
            'album': 'Album',
            'thumbnail_data': b'\xff\xd8\xff\xe0' + b'\x00' * 100,
        }
        writer.write_all(metadata)
        writer.save()

        reader = MetadataWriter(self.test_mp3)
        assert 'APIC:Cover' in reader.audio.tags

    def test_read_empty(self):
        writer = MetadataWriter(self.test_mp3)
        metadata = writer.read()
        assert metadata['title'] == ''
        assert metadata['artist'] == ''
        assert metadata['album'] == ''

    def test_overwrite_metadata(self):
        writer = MetadataWriter(self.test_mp3)
        writer.write_basic('First Title', 'First Artist', 'First Album')
        writer.save()

        writer2 = MetadataWriter(self.test_mp3)
        writer2.write_basic('Second Title', 'Second Artist', 'Second Album')
        writer2.save()

        reader = MetadataWriter(self.test_mp3)
        metadata = reader.read()
        assert metadata['title'] == 'Second Title'
        assert metadata['artist'] == 'Second Artist'
        assert metadata['album'] == 'Second Album'
