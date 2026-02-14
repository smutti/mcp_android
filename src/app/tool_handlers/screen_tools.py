from mcp.server.fastmcp import FastMCP, Image
from pydantic import Field

from errors import to_tool_error


def register_screen_tools(mcp: FastMCP, ctx, screen_service):
    @mcp.tool()
    def get_screenshot(
        serial: str | None = Field(default=None, description="Target device serial"),
        scale_factor: float = Field(default=0.4, description="Scale factor for returned screenshot"),
    ) -> Image:
        """Capture a screenshot from the target Android device."""
        try:
            def operation(session):
                png_bytes = screen_service.capture_png_bytes(session.adb_device, scale_factor=scale_factor)
                return Image(data=png_bytes, format="png")

            return ctx.run_for_device(serial, operation, requires_ui_lock=False)
        except Exception as error:
            raise to_tool_error(error) from error
