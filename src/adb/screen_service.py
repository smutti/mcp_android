from shared.serializers import image_to_png_bytes


class ScreenService:
    """Captures screenshots through adbutils and serializes them as PNG bytes."""

    @staticmethod
    def capture_png_bytes(device, scale_factor: float = 0.4) -> bytes:
        image = device.screenshot()
        return image_to_png_bytes(image, scale_factor=scale_factor)
