try:
    from mcp.server.fastmcp.exceptions import ToolError
except Exception:  # pragma: no cover - Fallback for local unit-test environments.
    class ToolError(Exception):
        """Fallback ToolError used when MCP package is not installed."""


class McpAndroidError(Exception):
    """Base class for MCP Android server errors."""


class DeviceResolutionError(McpAndroidError):
    """Raised when a target device cannot be resolved."""


class ValidationError(McpAndroidError):
    """Raised when tool parameters are invalid."""


class UiElementNotFoundError(McpAndroidError):
    """Raised when a UI selector does not match any element."""


def to_tool_error(error: Exception) -> ToolError:
    if isinstance(error, ToolError):
        return error
    return ToolError(str(error))
