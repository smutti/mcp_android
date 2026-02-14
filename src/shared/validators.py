from errors import ValidationError
from models.ui import POSSIBLE_UI_ATTRIBUTES


LOG_LEVEL_MAP = {
    "DEBUG": "D",
    "WARNING": "W",
    "ERROR": "E",
    "INFO": "I",
}


def validate_log_level(level: str) -> str:
    normalized = level.upper().strip()
    if normalized not in LOG_LEVEL_MAP:
        options = ", ".join(sorted(LOG_LEVEL_MAP))
        raise ValidationError(f"Invalid log level: {level}. Allowed values: {options}")
    return normalized


def parse_returned_attributes(returned_attributes: str) -> list[str]:
    attrs = [attribute.strip() for attribute in returned_attributes.split(",") if attribute.strip()]
    if not attrs:
        raise ValidationError("returned_attributes cannot be empty")

    invalid = [attr for attr in attrs if attr not in POSSIBLE_UI_ATTRIBUTES]
    if invalid:
        allowed = ", ".join(sorted(POSSIBLE_UI_ATTRIBUTES))
        raise ValidationError(f"Invalid attribute(s): {', '.join(invalid)}. Allowed values: {allowed}")
    return attrs
