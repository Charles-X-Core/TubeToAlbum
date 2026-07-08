import pytest
from core.thumbnail import ThumbnailHandler, crop_to_square, image_to_ico
from PIL import Image
import io


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
        img = Image.new('RGB', (1000, 1000), color='red')
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        image_data = output.getvalue()

        resized = self.handler.resize_image(image_data, max_size=(500, 500))

        resized_img = Image.open(io.BytesIO(resized))
        assert resized_img.width <= 500
        assert resized_img.height <= 500


class TestCropToSquare:
    def _make_image(self, w, h, color='red'):
        img = Image.new('RGB', (w, h), color=color)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        return output.getvalue()

    def test_already_square(self):
        data = self._make_image(500, 500, 'blue')
        result = crop_to_square(data)
        assert result == data

    def test_landscape_16_9(self):
        data = self._make_image(1920, 1080, 'green')
        result = crop_to_square(data)
        img = Image.open(io.BytesIO(result))
        assert img.width == 1080
        assert img.height == 1080

    def test_portrait_9_16(self):
        data = self._make_image(720, 1280, 'yellow')
        result = crop_to_square(data)
        img = Image.open(io.BytesIO(result))
        assert img.width == 720
        assert img.height == 720

    def test_very_wide(self):
        data = self._make_image(2000, 400, 'purple')
        result = crop_to_square(data)
        img = Image.open(io.BytesIO(result))
        assert img.width == 400
        assert img.height == 400

    def test_very_tall(self):
        data = self._make_image(300, 1500, 'orange')
        result = crop_to_square(data)
        img = Image.open(io.BytesIO(result))
        assert img.width == 300
        assert img.height == 300

    def test_crop_is_center(self):
        img = Image.new('RGB', (200, 100), color='black')
        pixels = img.load()
        pixels[100, 50] = (255, 0, 0)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        data = output.getvalue()

        result = crop_to_square(data)
        result_img = Image.open(io.BytesIO(result))
        assert result_img.width == 100
        assert result_img.height == 100

    def test_returns_bytes(self):
        data = self._make_image(800, 600)
        result = crop_to_square(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_output_is_jpeg(self):
        data = self._make_image(800, 600)
        result = crop_to_square(data)
        img = Image.open(io.BytesIO(result))
        assert img.format == 'JPEG'


class TestImageToIco:
    def _make_image(self, w, h, color='red'):
        img = Image.new('RGB', (w, h), color=color)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        return output.getvalue()

    def test_returns_bytes(self):
        data = self._make_image(720, 720)
        result = image_to_ico(data)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_output_is_ico(self):
        data = self._make_image(720, 720)
        result = image_to_ico(data)
        img = Image.open(io.BytesIO(result))
        assert img.format == 'ICO'

    def test_ico_sizes(self):
        data = self._make_image(720, 720)
        result = image_to_ico(data)
        img = Image.open(io.BytesIO(result))
        assert img.size == (256, 256)

    def test_from_jpg(self):
        data = self._make_image(1920, 1080)
        result = image_to_ico(data)
        assert len(result) > 0
        img = Image.open(io.BytesIO(result))
        assert img.format == 'ICO'

    def test_from_already_square(self):
        data = self._make_image(500, 500, 'blue')
        result = image_to_ico(data)
        assert len(result) > 0
