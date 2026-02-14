import unittest

from orchestration.session_manager import DeviceSessionManager


class FakeDeviceManager:
    def __init__(self, serials):
        self.serials = serials

    def list_serials(self):
        return list(self.serials)

    def get_device(self, serial):
        return {"serial": serial}


class FakeU2Provider:
    @staticmethod
    def connect(serial):
        return {"u2": serial}


class SessionManagerTest(unittest.TestCase):
    def test_session_manager_uses_default_serial(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A", "B"]),
            u2_client_provider=FakeU2Provider(),
            default_serial="B",
        )
        session = manager.get_session(None)
        self.assertEqual(session.serial, "B")

    def test_session_manager_reuses_cached_session(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"]),
            u2_client_provider=FakeU2Provider(),
            default_serial=None,
        )
        s1 = manager.get_session("A")
        s2 = manager.get_session("A")
        self.assertIs(s1, s2)

    def test_session_manager_active_sessions_sorted(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A", "B"]),
            u2_client_provider=FakeU2Provider(),
            default_serial=None,
        )
        manager.get_session("B")
        manager.get_session("A")
        self.assertEqual(manager.active_sessions(), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
