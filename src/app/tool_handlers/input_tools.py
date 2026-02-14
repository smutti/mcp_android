from mcp.server.fastmcp import FastMCP
from pydantic import Field

from errors import to_tool_error


def register_input_tools(mcp: FastMCP, ctx, interaction_service):
    @mcp.tool(structured_output=True)
    def tap_screen(
        serial: str | None = Field(default=None, description="Target device serial"),
        x: int = Field(description="Tap x coordinate"),
        y: int = Field(description="Tap y coordinate"),
    ) -> str:
        """Tap on a screen coordinate."""
        try:
            return ctx.run_for_device(serial, lambda s: interaction_service.tap(s.u2_device, x, y), requires_ui_lock=True)
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def swipe_screen(
        serial: str | None = Field(default=None, description="Target device serial"),
        x1: int = Field(description="Start x"),
        y1: int = Field(description="Start y"),
        x2: int = Field(description="End x"),
        y2: int = Field(description="End y"),
        duration_ms: int = Field(default=300, description="Swipe duration in milliseconds"),
    ) -> str:
        """Swipe from one coordinate to another."""
        try:
            return ctx.run_for_device(
                serial,
                lambda s: interaction_service.swipe(s.u2_device, x1, y1, x2, y2, duration_ms=duration_ms),
                requires_ui_lock=True,
            )
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def send_text(
        serial: str | None = Field(default=None, description="Target device serial"),
        text_to_send: str = Field(description="Text to type"),
        clear_existing: bool = Field(default=False, description="Clear current field before typing"),
    ) -> str:
        """Type text into the focused field."""
        try:
            return ctx.run_for_device(
                serial,
                lambda s: interaction_service.send_text(s.u2_device, text_to_send, clear=clear_existing),
                requires_ui_lock=True,
            )
        except Exception as error:
            raise to_tool_error(error) from error
