from io import BytesIO

from PIL import Image, UnidentifiedImageError

from app.core import settings


ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}

MAX_IMAGE_PIXELS = 20_000_000


def validate_image(image_bytes: bytes) -> str:
    """
    Validate image data before AWS processing.

    Returns the detected image format.
    Does not save the image to disk.
    """

    if not isinstance(image_bytes, bytes) or not image_bytes:
        raise ValueError("Image must contain valid bytes.")

    if len(image_bytes) > settings.MEDIA_MAX_IMAGE_BYTES:
        raise ValueError("Image exceeds the 5 MB limit.")

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise ValueError(
                    "Only JPEG and PNG images are supported."
                )

            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError(
                    "Image dimensions exceed the safety limit."
                )

            detected_format = image.format
            image.verify()

    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
    ) as exc:
        raise ValueError(
            "Invalid or unsafe image file."
        ) from exc

    return detected_format