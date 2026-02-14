from models.device import DeviceInfo


class DeviceManager:
    """Handles device discovery and metadata retrieval from adbutils."""

    def __init__(self, client_provider):
        self._client_provider = client_provider

    def list_devices(self) -> list[DeviceInfo]:
        devices = []
        for device in self._client_provider.list_devices():
            state = self._safe_get_state(device)
            model = self._safe_shell(device, "getprop ro.product.model")
            android_version = self._safe_shell(device, "getprop ro.build.version.release")
            devices.append(
                DeviceInfo(
                    serial=device.serial,
                    state=state,
                    model=model or None,
                    android_version=android_version or None,
                )
            )
        return devices

    def list_serials(self) -> list[str]:
        return [device.serial for device in self._client_provider.list_devices()]

    def get_device(self, serial: str):
        return self._client_provider.get_device(serial)

    @staticmethod
    def _safe_get_state(device) -> str:
        try:
            return device.get_state()
        except Exception:
            return "unknown"

    @staticmethod
    def _safe_shell(device, command: str) -> str:
        try:
            output = device.shell(command)
            return str(output).strip()
        except Exception:
            return ""
