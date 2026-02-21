import unittest
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from orchestration.session_manager import DeviceSessionManager


class FakeAdbDevice:
    def __init__(self, states=None):
        self._states = list(states or ["device"])
        self._index = 0

    def get_state(self):
        if self._index < len(self._states):
            state = self._states[self._index]
            self._index += 1
            return state
        return self._states[-1]


class FakeDeviceManager:
    def __init__(self, serials, device_factories=None):
        self.serials = serials
        self.device_factories = device_factories or {}
        self.get_device_calls = 0

    def list_serials(self):
        return list(self.serials)

    def get_device(self, serial):
        self.get_device_calls += 1
        factory = self.device_factories.get(serial)
        if factory:
            return factory()
        return FakeAdbDevice()


class FakeU2Provider:
    def __init__(self, fail_connect_times=0, sleep_on_connect_s=0.0):
        self.fail_connect_times = fail_connect_times
        self.sleep_on_connect_s = sleep_on_connect_s
        self.connect_calls = 0

    def connect(self, serial):
        self.connect_calls += 1
        if self.sleep_on_connect_s > 0:
            sleep(self.sleep_on_connect_s)
        if self.connect_calls <= self.fail_connect_times:
            raise RuntimeError("uiautomator transport error")
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

    def test_session_manager_retries_connection_and_recovers(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"]),
            u2_client_provider=FakeU2Provider(fail_connect_times=1),
            default_serial=None,
            connect_retries=2,
            connect_backoff_s=0.0,
        )
        session = manager.get_session("A")
        self.assertEqual(session.serial, "A")
        self.assertEqual(manager._u2_client_provider.connect_calls, 2)

    def test_session_manager_reconnects_if_cached_session_unhealthy(self):
        created = 0

        def factory():
            nonlocal created
            created += 1
            if created == 1:
                return FakeAdbDevice(states=["offline"])
            return FakeAdbDevice(states=["device"])

        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"], device_factories={"A": factory}),
            u2_client_provider=FakeU2Provider(),
            default_serial=None,
            healthcheck_interval_s=0.0,
        )

        session = manager.get_session("A")
        self.assertEqual(session.serial, "A")
        self.assertEqual(created, 2)

    def test_session_manager_eviction_on_ttl(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"]),
            u2_client_provider=FakeU2Provider(),
            default_serial=None,
            session_ttl_s=0.01,
            healthcheck_interval_s=3600.0,
        )
        s1 = manager.get_session("A")
        sleep(0.02)
        s2 = manager.get_session("A")
        self.assertIsNot(s1, s2)

    def test_session_manager_fallback_when_default_serial_disconnected(self):
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"]),
            u2_client_provider=FakeU2Provider(),
            default_serial="B",
        )
        session = manager.get_session(None)
        self.assertEqual(session.serial, "A")

    def test_session_manager_creates_single_session_under_concurrency(self):
        provider = FakeU2Provider(sleep_on_connect_s=0.05)
        manager = DeviceSessionManager(
            device_manager=FakeDeviceManager(["A"]),
            u2_client_provider=provider,
            default_serial=None,
            healthcheck_interval_s=3600.0,
        )

        with ThreadPoolExecutor(max_workers=2) as pool:
            future_1 = pool.submit(manager.get_session, "A")
            future_2 = pool.submit(manager.get_session, "A")
            s1 = future_1.result()
            s2 = future_2.result()

        self.assertIs(s1, s2)
        self.assertEqual(provider.connect_calls, 1)


if __name__ == "__main__":
    unittest.main()
