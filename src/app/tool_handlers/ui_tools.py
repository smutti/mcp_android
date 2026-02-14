from mcp.server.fastmcp import FastMCP
from pydantic import Field

from errors import to_tool_error
from shared.validators import parse_returned_attributes


def register_ui_tools(mcp: FastMCP, ctx, hierarchy_service, selector_service):
    @mcp.tool(structured_output=True)
    def get_ui_dump(
        serial: str | None = Field(default=None, description="Target device serial"),
        returned_attributes: str = Field(
            description=(
                "Comma-separated attributes to keep for each XML node. "
                "Example: text,resource-id,bounds,class"
            )
        ),
    ) -> str:
        """Get filtered XML hierarchy from the current device screen."""
        try:
            attributes_to_keep = parse_returned_attributes(returned_attributes)

            def operation(session):
                return hierarchy_service.get_filtered_dump(session.u2_device, attributes_to_keep)

            return ctx.run_for_device(serial, operation, requires_ui_lock=True)
        except Exception as error:
            raise to_tool_error(error) from error

    @mcp.tool(structured_output=True)
    def click_ui_element(
        serial: str | None = Field(default=None, description="Target device serial"),
        text: str | None = Field(default=None, description="Element text selector"),
        resource_id: str | None = Field(default=None, description="Element resource-id selector"),
        content_desc: str | None = Field(default=None, description="Element content-desc selector"),
        timeout_s: float = Field(default=10.0, description="Selector wait timeout in seconds"),
    ) -> str:
        """Click a UI element selected by exactly one selector."""
        try:
            def operation(session):
                return selector_service.click(
                    session.u2_device,
                    text=text,
                    resource_id=resource_id,
                    content_desc=content_desc,
                    timeout_s=timeout_s,
                )

            return ctx.run_for_device(serial, operation, requires_ui_lock=True)
        except Exception as error:
            raise to_tool_error(error) from error
