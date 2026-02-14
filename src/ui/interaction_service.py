from errors import ValidationError


class InteractionService:
    """Implements UI gestures and text interactions."""

    @staticmethod
    def tap(u2_device, x: int, y: int) -> str:
        u2_device.click(x, y)
        return f"Tapped at ({x}, {y})"

    @staticmethod
    def swipe(u2_device, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> str:
        if duration_ms <= 0:
            raise ValidationError("duration_ms must be > 0")
        u2_device.swipe(x1, y1, x2, y2, duration=duration_ms / 1000)
        return f"Swiped from ({x1}, {y1}) to ({x2}, {y2})"

    @staticmethod
    def send_text(u2_device, text: str, clear: bool = False) -> str:
        if not text:
            raise ValidationError("text_to_send cannot be empty")
        u2_device.send_keys(text, clear=clear)
        return f"Sent text: {text}"

    @staticmethod
    def system_action(u2_device, action: str) -> str:
        action_map = {
            "BACK": "back",
            "HOME": "home",
            "RECENT_APPS": "recent",
        }
        normalized = action.upper().strip()
        if normalized not in action_map:
            raise ValidationError("Invalid action. Allowed values: BACK, HOME, RECENT_APPS")
        u2_device.press(action_map[normalized])
        return f"Performed action: {normalized}"
