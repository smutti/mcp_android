import io

from PIL import Image as PILImage


def image_to_png_bytes(image: PILImage.Image, scale_factor: float = 1.0) -> bytes:
    if scale_factor <= 0:
        raise ValueError("scale_factor must be > 0")

    output_image = image
    if scale_factor != 1.0:
        width = max(1, int(image.width * scale_factor))
        height = max(1, int(image.height * scale_factor))
        output_image = image.resize((width, height))

    buffer = io.BytesIO()
    output_image.save(buffer, format="PNG")
    return buffer.getvalue()
