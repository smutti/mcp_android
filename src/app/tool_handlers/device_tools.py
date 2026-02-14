from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import Field

from errors import to_tool_error
from models.device import DeviceInfo


def register_device_tools(mcp: FastMCP, ctx, device_manager):
    @mcp.tool(structured_output=True)
    def list_devices() -> list[DeviceInfo]:
        """List all connected Android devices."""
        try:
            return device_manager.list_devices()
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def get_device_status(
        serial: str = Field(description="Target device serial"),
    ) -> DeviceInfo:
        """Get status and metadata for a specific device."""
        try:
            devices = {d.serial: d for d in device_manager.list_devices()}
            if serial not in devices:
                raise ToolError(f"Device not found: {serial}")
            return devices[serial]
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def clear_device_session(
        serial: str = Field(description="Target device serial"),
    ) -> str:
        """Clear a cached device session."""
        try:
            removed = ctx.session_manager.clear_session(serial)
            return f"Session cleared for {serial}" if removed else f"No active session for {serial}"
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def list_active_sessions() -> list[str]:
        """List serial numbers with an active MCP session."""
        try:
            return ctx.session_manager.active_sessions()
        except Exception as error:
            raise to_tool_error(error) from error
