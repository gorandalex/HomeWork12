import cloudinary.uploader

from unittest import TestCase
from unittest.mock import patch

from src.services.upload_avatar import UploadService


class MockedUploader:
    @staticmethod
    def upload(file, public_id, overwrite=True):
        return {"url": f"https://example.com/{public_id}", "version": "mocked_version"}

    @staticmethod
    def build_url(public_id, width, height, crop, version):
        return f"https://example.com/{public_id}?w={width}&h={height}&crop={crop}&v={version}"


class TestUploadService(TestCase):
    def test_create_name_avatar(self):
        email = "test@example.com"
        prefix = "avatars"
        expected_name = "avatars/973dfe463ec8"
        self.assertEqual(UploadService.create_name_avatar(email, prefix), expected_name)

    @patch.object(cloudinary.uploader, "upload", MockedUploader.upload)
    def test_upload(self):
        file = "test.jpg"
        public_id = "abc123"
        expected_url = "https://example.com/abc123"
        expected_version = "mocked_version"

        url = UploadService.upload(file, public_id)
        self.assertEqual(url["url"], expected_url)
        self.assertEqual(url["version"], expected_version)

    @patch.object(cloudinary.CloudinaryImage, "build_url", MockedUploader.build_url)
    def test_get_url_avatar(self):
        public_id = "abc123"
        version = "mocked_version"
        expected_url = "https://example.com/abc123?w=250&h=250&crop=fill&v=mocked_version"

        url = UploadService.get_url_avatar(public_id, version)
        self.assertEqual(url, expected_url)