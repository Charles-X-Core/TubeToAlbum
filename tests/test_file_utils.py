import pytest
import os
import tempfile
import shutil
from utils.file_utils import (
    ensure_directory, get_file_extension, get_file_size,
    format_file_size, safe_filename, file_exists, delete_file
)


class TestFileUtils:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_ensure_directory(self):
        test_dir = os.path.join(self.temp_dir, 'new_dir')
        ensure_directory(test_dir)
        assert os.path.exists(test_dir)

    def test_ensure_directory_nested(self):
        test_dir = os.path.join(self.temp_dir, 'parent', 'child')
        ensure_directory(test_dir)
        assert os.path.exists(test_dir)

    def test_get_file_extension(self):
        assert get_file_extension('test.mp3') == 'mp3'
        assert get_file_extension('test.m4a') == 'm4a'
        assert get_file_extension('test.flac') == 'flac'
        assert get_file_extension('test') == ''

    def test_get_file_size(self):
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Hello World')
        assert get_file_size(test_file) == 11

    def test_get_file_size_nonexistent(self):
        assert get_file_size('/nonexistent/file.txt') == 0

    def test_format_file_size(self):
        assert format_file_size(1023) == '1023.0 B'
        assert format_file_size(1024) == '1.0 KB'
        assert format_file_size(1048576) == '1.0 MB'
        assert format_file_size(1073741824) == '1.0 GB'

    def test_safe_filename(self):
        assert safe_filename('Test: File Name') == 'Test File Name'
        assert safe_filename('Test/File\\Name') == 'TestFileName'
        assert safe_filename('Test<>File') == 'TestFile'
        assert safe_filename('  Test  File  ') == 'Test File'

    def test_file_exists(self):
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        assert file_exists(test_file) is True

    def test_file_exists_nonexistent(self):
        assert file_exists('/nonexistent/file.txt') is False

    def test_delete_file(self):
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        assert delete_file(test_file) is True
        assert not os.path.exists(test_file)

    def test_delete_file_nonexistent(self):
        assert delete_file('/nonexistent/file.txt') is False
