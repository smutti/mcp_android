from threading import Lock
from time import monotonic, sleep

from errors import DeviceResolutionError
from orchestration.device_session import DeviceSession


class DeviceSessionManager:
    """Creates and caches per-device sessions in a thread-safe way."""

    def __init__(
        self,
        device_manager,
        u2_client_provider,
        default_serial: str | None = None,
        session_ttl_s: float = 900.0,
        healthcheck_interval_s: float = 5.0,
        connect_retries: int = 2,
        connect_backoff_s: float = 0.25,
    ):
        self._device_manager = device_manager
        self._u2_client_provider = u2_client_provider
        self._default_serial = default_serial
        self._session_ttl_s = session_ttl_s
        self._healthcheck_interval_s = healthcheck_interval_s
        self._connect_retries = connect_retries
        self._connect_backoff_s = connect_backoff_s
        self._sessions: dict[str, DeviceSession] = {}
        self._lock = Lock()

    def resolve_serial(self, serial: str | None) -> str:
        serials = self._device_manager.list_serials()

        if serial:
            if serial not in serials:
                raise DeviceResolutionError(f"Device not found: {serial}")
            return serial
        if self._default_serial and self._default_serial in serials:
            return self._default_serial

        if len(serials) == 1:
            return serials[0]
        if not serials:
            raise DeviceResolutionError("No connected Android devices found")
        raise DeviceResolutionError("Multiple devices connected. Please specify serial")

    def get_session(self, serial: str | None) -> DeviceSession:
        resolved_serial = self.resolve_serial(serial)
        with self._lock:
            session = self._sessions.get(resolved_serial)
            now = monotonic()

            if session and self._is_expired(session, now):
                self._sessions.pop(resolved_serial, None)
                session = None

            if session is None:
                session = self._create_session_with_retry(resolved_serial)
                self._sessions[resolved_serial] = session

            if self._needs_health_check(session, now) and not self._is_session_healthy(session, now):
                self._sessions.pop(resolved_serial, None)
                session = self._create_session_with_retry(resolved_serial)
                self._sessions[resolved_serial] = session

            session.touch(now)
            return session

    def clear_session(self, serial: str) -> bool:
        with self._lock:
            return self._sessions.pop(serial, None) is not None

    def active_sessions(self) -> list[str]:
        with self._lock:
            return sorted(self._sessions.keys())

    def should_retry_after_error(self, error: Exception) -> bool:
        if isinstance(error, (ConnectionError, TimeoutError, OSError)):
            return True

        error_text = str(error).lower()
        transient_markers = (
            "device offline",
            "connection reset",
            "connection aborted",
            "connection refused",
            "transport",
            "socket",
            "rpc",
            "uiautomator",
            "adb",
            "timed out",
            "timeout",
        )
        return any(marker in error_text for marker in transient_markers)

    def _create_session_with_retry(self, serial: str) -> DeviceSession:
        attempts = max(1, self._connect_retries + 1)
        last_error: Exception | None = None

        for attempt in range(attempts):
            try:
                adb_device = self._device_manager.get_device(serial)
                u2_device = self._u2_client_provider.connect(serial)
                return DeviceSession(serial=serial, adb_device=adb_device, u2_device=u2_device)
            except Exception as error:
                last_error = error
                if attempt < attempts - 1:
                    backoff = self._connect_backoff_s * (2**attempt)
                    sleep(backoff)

        raise DeviceResolutionError(f"Unable to create session for {serial}: {last_error}") from last_error

    def _is_expired(self, session: DeviceSession, now: float) -> bool:
        return self._session_ttl_s > 0 and (now - session.last_used_at) > self._session_ttl_s

    def _needs_health_check(self, session: DeviceSession, now: float) -> bool:
        if self._healthcheck_interval_s <= 0:
            return True
        return (now - session.last_health_check_at) >= self._healthcheck_interval_s

    def _is_session_healthy(self, session: DeviceSession, now: float) -> bool:
        adb_healthy = self._check_adb_health(session.adb_device)
        u2_healthy = self._check_u2_health(session.u2_device)

        if adb_healthy and u2_healthy:
            session.mark_health_ok(now)
            return True

        session.mark_health_failure(now)
        return False

    @staticmethod
    def _check_adb_health(adb_device) -> bool:
        get_state = getattr(adb_device, "get_state", None)
        if callable(get_state):
            try:
                state = str(get_state()).strip().lower()
                return state not in {"offline", "unknown"}
            except Exception:
                return False
        return True

    @staticmethod
    def _check_u2_health(u2_device) -> bool:
        for attribute in ("info", "window_size"):
            member = getattr(u2_device, attribute, None)
            if member is None:
                continue
            try:
                member() if callable(member) else bool(member)
                return True
            except Exception:
                return False
        return True
