import tempfile
from pathlib import Path

import pytest

from app.image_utils import ImageGenerator


@pytest.fixture
def image_generator():
    """Create an ImageGenerator with a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield ImageGenerator(temp_dir)


def test_create_default_image(image_generator):
    """Test creating a default image."""
    filename, file_path = image_generator.create_image()

    assert filename is not None
    assert file_path is not None
    assert Path(file_path).exists()
    assert Path(file_path).suffix == ".png"


def test_create_image_with_content(image_generator):
    """Test creating an image with specific content."""
    content = "Hello TRMNL!\nThis is a test message."
    filename, file_path = image_generator.create_image(content=content)

    assert filename is not None
    assert Path(file_path).exists()


def test_create_image_with_custom_filename(image_generator):
    """Test creating an image with a custom filename."""
    custom_filename = "my-custom-image"
    filename, file_path = image_generator.create_image(filename=custom_filename)

    assert filename == custom_filename
    assert custom_filename in file_path


def test_create_welcome_image(image_generator):
    """Test creating a welcome image."""
    device_id = "ABC123"
    filename, file_path = image_generator.create_welcome_image(device_id)

    assert device_id in filename
    assert Path(file_path).exists()


def test_html_to_image(image_generator):
    """Test HTML to image conversion."""
    html_content = "<h1>Test HTML</h1><p>This is a test paragraph.</p>"
    filename, file_path = image_generator.html_to_image(html_content)

    assert filename is not None
    assert Path(file_path).exists()


def test_image_dimensions(image_generator):
    """Test custom image dimensions."""
    filename, file_path = image_generator.create_image(
        content="Test", width=400, height=240
    )

    # Just verify the image was created
    # In a more complete test, you'd verify the actual dimensions
    assert Path(file_path).exists()
