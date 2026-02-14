from threading import Lock

from errors import DeviceResolutionError
from orchestration.device_session import DeviceSession


class DeviceSessionManager:
    """Creates and caches per-device sessions in a thread-safe way."""

    def __init__(self, device_manager, u2_client_provider, default_serial: str | None = None):
        self._device_manager = device_manager
        self._u2_client_provider = u2_client_provider
        self._default_serial = default_serial
        self._sessions: dict[str, DeviceSession] = {}
        self._lock = Lock()

    def resolve_serial(self, serial: str | None) -> str:
        if serial:
            return serial
        if self._default_serial:
            return self._default_serial

        serials = self._device_manager.list_serials()
        if len(serials) == 1:
            return serials[0]
        if not serials:
            raise DeviceResolutionError("No connected Android devices found")
        raise DeviceResolutionError("Multiple devices connected. Please specify serial")

    def get_session(self, serial: str | None) -> DeviceSession:
        resolved_serial = self.resolve_serial(serial)
        with self._lock:
            if resolved_serial not in self._sessions:
                adb_device = self._device_manager.get_device(resolved_serial)
                u2_device = self._u2_client_provider.connect(resolved_serial)
                self._sessions[resolved_serial] = DeviceSession(
                    serial=resolved_serial,
                    adb_device=adb_device,
                    u2_device=u2_device,
                )
            return self._sessions[resolved_serial]

    def clear_session(self, serial: str) -> bool:
        with self._lock:
            return self._sessions.pop(serial, None) is not None

    def active_sessions(self) -> list[str]:
        with self._lock:
            return sorted(self._sessions.keys())
