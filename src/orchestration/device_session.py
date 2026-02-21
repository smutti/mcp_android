from dataclasses import dataclass, field
from threading import RLock
import time


@dataclass
class DeviceSession:
    serial: str
    adb_device: object
    u2_device: object
    ui_lock: RLock = field(default_factory=RLock)
    created_at: float = field(default_factory=time.monotonic)
    last_used_at: float = field(default_factory=time.monotonic)
    last_health_check_at: float = 0.0
    consecutive_failures: int = 0

    def touch(self, now: float | None = None) -> None:
        self.last_used_at = time.monotonic() if now is None else now

    def mark_health_ok(self, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        self.last_health_check_at = current
        self.consecutive_failures = 0

    def mark_health_failure(self, now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        self.last_health_check_at = current
        self.consecutive_failures += 1
