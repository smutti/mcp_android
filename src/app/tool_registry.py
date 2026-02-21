from mcp.server.fastmcp import FastMCP

from adb.client import AdbClientProvider
from adb.device_manager import DeviceManager
from adb.logcat_service import LogcatService
from adb.screen_service import ScreenService
from app.context import AppContext
from app.tool_handlers.device_tools import register_device_tools
from app.tool_handlers.input_tools import register_input_tools
from app.tool_handlers.log_tools import register_log_tools
from app.tool_handlers.screen_tools import register_screen_tools
from app.tool_handlers.system_tools import register_system_tools
from app.tool_handlers.ui_tools import register_ui_tools
from orchestration.executor import DeviceExecutor
from orchestration.session_manager import DeviceSessionManager
from ui.hierarchy_service import HierarchyService
from ui.interaction_service import InteractionService
from ui.selector_service import SelectorService
from ui.u2_client import U2ClientProvider


def create_mcp_server(
    default_serial: str | None,
    max_workers: int,
    port: int,
    session_ttl_s: float = 900.0,
    healthcheck_interval_s: float = 5.0,
    connect_retries: int = 2,
    connect_backoff_s: float = 0.25,
) -> FastMCP:
    mcp = FastMCP(name="MCP Android Server", port=port)

    adb_provider = AdbClientProvider()
    device_manager = DeviceManager(adb_provider)
    u2_provider = U2ClientProvider()

    session_manager = DeviceSessionManager(
        device_manager,
        u2_provider,
        default_serial=default_serial,
        session_ttl_s=session_ttl_s,
        healthcheck_interval_s=healthcheck_interval_s,
        connect_retries=connect_retries,
        connect_backoff_s=connect_backoff_s,
    )
    executor = DeviceExecutor(max_workers=max_workers)
    ctx = AppContext(session_manager=session_manager, executor=executor)

    register_device_tools(mcp, ctx, device_manager)
    register_log_tools(mcp, ctx, LogcatService())
    register_screen_tools(mcp, ctx, ScreenService())
    register_ui_tools(mcp, ctx, HierarchyService(), SelectorService())
    register_input_tools(mcp, ctx, InteractionService())
    register_system_tools(mcp, ctx, InteractionService())

    return mcp
