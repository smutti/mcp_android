from mcp.server.fastmcp import FastMCP
from pydantic import Field

from errors import to_tool_error
from shared.validators import validate_log_level


def register_log_tools(mcp: FastMCP, ctx, logcat_service):
    @mcp.tool(structured_output=True)
    def get_logcat_output(
        serial: str | None = Field(default=None, description="Target device serial"),
        app_package: str = Field(description="App package to filter logcat by process pid"),
        log_level: str = Field(default="DEBUG", description="DEBUG, INFO, WARNING, ERROR"),
        max_lines: int = Field(default=100, description="Maximum lines returned"),
    ) -> str:
        """Get app-specific logcat lines from a target Android device."""
        try:
            normalized_level = validate_log_level(log_level)

            def operation(session):
                return logcat_service.get_for_package(
                    session.adb_device,
                    app_package=app_package,
                    level=normalized_level,
                    max_lines=max_lines,
                )

            return ctx.run_for_device(serial, operation, requires_ui_lock=False)
        except Exception as error:
            raise to_tool_error(error) from error
