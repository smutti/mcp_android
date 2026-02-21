from orchestration.executor import DeviceExecutor
from orchestration.session_manager import DeviceSessionManager


class AppContext:
    """Application context shared across MCP tool handlers."""

    def __init__(self, session_manager: DeviceSessionManager, executor: DeviceExecutor):
        self.session_manager = session_manager
        self.executor = executor

    def run_for_device(self, serial, operation, requires_ui_lock: bool = False):
        session = self.session_manager.get_session(serial)
        try:
            return self.executor.run(session, operation, requires_ui_lock=requires_ui_lock)
        except Exception as error:
            if not self.session_manager.should_retry_after_error(error):
                raise
            self.session_manager.clear_session(session.serial)
            refreshed_session = self.session_manager.get_session(session.serial)
            return self.executor.run(refreshed_session, operation, requires_ui_lock=requires_ui_lock)
