from dataclasses import dataclass, field
from threading import RLock


@dataclass
class DeviceSession:
    serial: str
    adb_device: object
    u2_device: object
    ui_lock: RLock = field(default_factory=RLock)
