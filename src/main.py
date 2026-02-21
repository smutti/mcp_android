from app.tool_registry import create_mcp_server
from config import parse_args


def run() -> None:
    settings = parse_args()
    mcp = create_mcp_server(
        default_serial=settings.default_serial,
        max_workers=settings.max_workers,
        port=settings.port,
        session_ttl_s=settings.session_ttl_s,
        healthcheck_interval_s=settings.healthcheck_interval_s,
        connect_retries=settings.connect_retries,
        connect_backoff_s=settings.connect_backoff_s,
    )

    if settings.mode == "stdio":
        mcp.run(transport="stdio")
    elif settings.mode == "streamable-http":
        mcp.run(transport="streamable-http")
    elif settings.mode == "sse":
        mcp.run(transport="sse")
    else:
        raise ValueError(f"Unsupported mode: {settings.mode}")


if __name__ == "__main__":
    run()
