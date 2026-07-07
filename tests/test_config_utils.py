import pytest
import os
import tempfile
import shutil
from utils.config_utils import load_config, save_config, merge_configs, get_config_value, DEFAULT_CONFIG


class TestConfigUtils:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_load_config_default(self):
        config = load_config()
        assert config['default_quality'] == '192'
        assert config['default_format'] == 'mp3'

    def test_load_config_from_file(self):
        config_path = os.path.join(self.temp_dir, 'config.json')
        user_config = {
            'default_quality': '320',
            'metadata': {
                'default_genre': 'Rock'
            }
        }
        save_config(user_config, config_path)

        config = load_config(config_path)
        assert config['default_quality'] == '320'
        assert config['metadata']['default_genre'] == 'Rock'

    def test_load_config_nonexistent(self):
        config = load_config('/nonexistent/config.json')
        assert config['default_quality'] == '192'

    def test_save_config(self):
        config_path = os.path.join(self.temp_dir, 'config.json')
        config = {'test': 'value'}
        save_config(config, config_path)
        assert os.path.exists(config_path)

    def test_save_config_creates_directory(self):
        config_path = os.path.join(self.temp_dir, 'subdir', 'config.json')
        config = {'test': 'value'}
        save_config(config, config_path)
        assert os.path.exists(config_path)

    def test_merge_configs(self):
        base = {'a': 1, 'b': {'c': 2, 'd': 3}}
        override = {'b': {'c': 10}, 'e': 5}
        result = merge_configs(base, override)
        assert result['a'] == 1
        assert result['b']['c'] == 10
        assert result['b']['d'] == 3
        assert result['e'] == 5

    def test_get_config_value(self):
        config = {'a': {'b': {'c': 42}}}
        assert get_config_value(config, 'a.b.c') == 42

    def test_get_config_value_default(self):
        config = {'a': 1}
        assert get_config_value(config, 'b.c', default='not found') == 'not found'

    def test_default_config_structure(self):
        assert 'default_quality' in DEFAULT_CONFIG
        assert 'metadata' in DEFAULT_CONFIG
        assert 'download' in DEFAULT_CONFIG
