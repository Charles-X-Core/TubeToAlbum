import pytest
from core.thumbnail import ThumbnailHandler


class TestThumbnailHandler:
    def setup_method(self):
        self.handler = ThumbnailHandler()

    def test_get_video_id_standard(self):
        url = 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ'
        video_id = self.handler.get_video_id(url)
        assert video_id == 'fJ9rUzIMcZQ'

    def test_get_video_id_short(self):
        url = 'https://youtu.be/fJ9rUzIMcZQ'
        video_id = self.handler.get_video_id(url)
        assert video_id == 'fJ9rUzIMcZQ'

    def test_get_video_id_embed(self):
        url = 'https://www.youtube.com/embed/fJ9rUzIMcZQ'
        video_id = self.handler.get_video_id(url)
        assert video_id == 'fJ9rUzIMcZQ'

    def test_get_video_id_invalid(self):
        url = 'https://www.example.com/video'
        video_id = self.handler.get_video_id(url)
        assert video_id is None

    def test_thumbnail_urls(self):
        assert 'maxresdefault' in self.handler.YOUTUBE_THUMBNAIL_URLS
        assert 'sddefault' in self.handler.YOUTUBE_THUMBNAIL_URLS
        assert 'hqdefault' in self.handler.YOUTUBE_THUMBNAIL_URLS
        assert 'mqdefault' in self.handler.YOUTUBE_THUMBNAIL_URLS
        assert 'default' in self.handler.YOUTUBE_THUMBNAIL_URLS

    def test_resize_image(self):
        from PIL import Image
        import io

        img = Image.new('RGB', (1000, 1000), color='red')
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        image_data = output.getvalue()

        resized = self.handler.resize_image(image_data, max_size=(500, 500))

        resized_img = Image.open(io.BytesIO(resized))
        assert resized_img.width <= 500
        assert resized_img.height <= 500
