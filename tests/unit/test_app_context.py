import unittest
from types import SimpleNamespace

from app.context import AppContext


class FakeSessionManager:
    def __init__(self):
        self.sessions = [SimpleNamespace(serial="A"), SimpleNamespace(serial="A")]
        self.get_calls = 0
        self.clear_calls = 0
        self.retryable = True

    def get_session(self, serial):
        session = self.sessions[min(self.get_calls, len(self.sessions) - 1)]
        self.get_calls += 1
        return session

    def clear_session(self, serial):
        self.clear_calls += 1
        return True

    def should_retry_after_error(self, error):
        return self.retryable


class FakeExecutor:
    def __init__(self):
        self.calls = 0

    def run(self, session, operation, requires_ui_lock=False):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("uiautomator transport error")
        return operation(session)


class AppContextTest(unittest.TestCase):
    def test_run_for_device_retries_once_on_transient_error(self):
        session_manager = FakeSessionManager()
        executor = FakeExecutor()
        ctx = AppContext(session_manager=session_manager, executor=executor)

        result = ctx.run_for_device("A", lambda s: f"ok:{s.serial}")

        self.assertEqual(result, "ok:A")
        self.assertEqual(executor.calls, 2)
        self.assertEqual(session_manager.clear_calls, 1)

    def test_run_for_device_does_not_retry_non_transient(self):
        session_manager = FakeSessionManager()
        session_manager.retryable = False
        executor = FakeExecutor()
        ctx = AppContext(session_manager=session_manager, executor=executor)

        with self.assertRaises(RuntimeError):
            ctx.run_for_device("A", lambda s: f"ok:{s.serial}")
        self.assertEqual(executor.calls, 1)
        self.assertEqual(session_manager.clear_calls, 0)


if __name__ == "__main__":
    unittest.main()
