from io import BytesIO

import pytest
from PIL import Image

from app.services.image_validation import validate_image


def create_test_image(
    image_format="PNG",
    size=(100, 100),
):
    """Create a synthetic image without personal data."""

    image = Image.new(
        "RGB",
        size,
        color="blue",
    )

    buffer = BytesIO()
    image.save(buffer, format=image_format)

    return buffer.getvalue()


def test_valid_png_image():
    image_bytes = create_test_image("PNG")

    result = validate_image(image_bytes)

    assert result == "PNG"


def test_valid_jpeg_image():
    image_bytes = create_test_image("JPEG")

    result = validate_image(image_bytes)

    assert result == "JPEG"


def test_reject_empty_image():
    with pytest.raises(ValueError):
        validate_image(b"")


def test_reject_invalid_image():
    with pytest.raises(ValueError):
        validate_image(b"this-is-not-an-image")


def test_reject_unsupported_format():
    image_bytes = create_test_image("GIF")

    with pytest.raises(
        ValueError,
        match="Only JPEG and PNG",
    ):
        validate_image(image_bytes)


def test_reject_oversized_image():
    image_bytes = b"x" * (5 * 1024 * 1024 + 1)

    with pytest.raises(
        ValueError,
        match="5 MB",
    ):
        validate_image(image_bytes)


def test_reject_corrupted_image():
    image_bytes = create_test_image("PNG")

    corrupted_image = image_bytes[:20]

    with pytest.raises(ValueError):
        validate_image(corrupted_image)
def test_reject_image_with_excessive_dimensions():
    image_bytes = create_test_image(
        image_format="PNG",
        size=(5000, 5000),
    )

    with pytest.raises(
        ValueError,
        match="Image dimensions exceed the safety limit",
    ):
        validate_image(image_bytes)