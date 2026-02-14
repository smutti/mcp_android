from mcp.server.fastmcp import FastMCP
from pydantic import Field

from errors import to_tool_error


def register_system_tools(mcp: FastMCP, ctx, interaction_service):
    @mcp.tool(structured_output=True)
    def perform_system_action(
        serial: str | None = Field(default=None, description="Target device serial"),
        action: str = Field(description="BACK, HOME, RECENT_APPS"),
    ) -> str:
        """Perform a global Android system action."""
        try:
            return ctx.run_for_device(
                serial,
                lambda s: interaction_service.system_action(s.u2_device, action),
                requires_ui_lock=True,
            )
        except Exception as error:
            raise to_tool_error(error) from error
