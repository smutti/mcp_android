import argparse
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str
    port: int
    default_serial: str | None
    max_workers: int


def parse_args() -> Settings:
    parser = argparse.ArgumentParser(description="Multi-device Android MCP Server")
    parser.add_argument(
        "--mode",
        dest="mode",
        choices=["stdio", "streamable-http", "sse"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="MCP transport mode",
    )
    parser.add_argument(
        "--port",
        dest="port",
        type=int,
        default=int(os.getenv("MCP_PORT", "3001")),
        help="Port used by HTTP/SSE transports",
    )
    parser.add_argument(
        "--default-serial",
        dest="default_serial",
        default=os.getenv("MCP_DEFAULT_SERIAL"),
        help="Default device serial if omitted by tools",
    )
    parser.add_argument(
        "--max-workers",
        dest="max_workers",
        type=int,
        default=int(os.getenv("MCP_MAX_WORKERS", "8")),
        help="Worker threads for parallel tool execution",
    )
    args = parser.parse_args()

    if args.port <= 0:
        raise ValueError("Port must be > 0")
    if args.max_workers <= 0:
        raise ValueError("max-workers must be > 0")

    return Settings(
        mode=args.mode,
        port=args.port,
        default_serial=args.default_serial,
        max_workers=args.max_workers,
    )
