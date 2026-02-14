from adbutils import adb


class AdbClientProvider:
    """Thin wrapper around adbutils global client."""

    def list_devices(self):
        return adb.device_list()

    def get_device(self, serial: str):
        return adb.device(serial=serial)
