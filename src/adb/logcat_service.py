import shlex

from errors import ValidationError
from shared.validators import LOG_LEVEL_MAP


class LogcatService:
    """Retrieves app-specific logcat data."""

    @staticmethod
    def get_for_package(device, app_package: str, level: str, max_lines: int = 100) -> str:
        if not app_package.strip():
            raise ValidationError("app_package cannot be empty")
        if max_lines <= 0:
            raise ValidationError("max_lines must be > 0")

        pid_command = f"pidof -s {shlex.quote(app_package)}"
        pid = str(device.shell(pid_command)).strip()
        if not pid:
            raise ValidationError(f"App with package '{app_package}' not running or not found")

        log_level = LOG_LEVEL_MAP[level]
        log_output = str(device.shell(f"logcat -d -b default *:{log_level}"))
        filtered = [line for line in log_output.splitlines() if pid in line]
        return "\n".join(filtered[-max_lines:])
