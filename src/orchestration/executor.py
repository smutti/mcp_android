from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext


class DeviceExecutor:
    """Runs operations in a thread pool and serializes UI operations per device."""

    def __init__(self, max_workers: int = 8):
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    def run(self, session, func, requires_ui_lock: bool = False):
        lock_context = session.ui_lock if requires_ui_lock else nullcontext()

        def task():
            with lock_context:
                return func(session)

        future = self._pool.submit(task)
        return future.result()
