import argparse
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str
    port: int
    default_serial: str | None
    max_workers: int
    session_ttl_s: float
    healthcheck_interval_s: float
    connect_retries: int
    connect_backoff_s: float


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
    parser.add_argument(
        "--session-ttl-s",
        dest="session_ttl_s",
        type=float,
        default=float(os.getenv("MCP_SESSION_TTL_S", "900")),
        help="Evict cached sessions after this inactivity TTL in seconds (<=0 disables TTL eviction)",
    )
    parser.add_argument(
        "--healthcheck-interval-s",
        dest="healthcheck_interval_s",
        type=float,
        default=float(os.getenv("MCP_HEALTHCHECK_INTERVAL_S", "5")),
        help="Minimum interval in seconds between cached session health checks (<=0 checks every time)",
    )
    parser.add_argument(
        "--connect-retries",
        dest="connect_retries",
        type=int,
        default=int(os.getenv("MCP_CONNECT_RETRIES", "2")),
        help="Number of retries when creating a device session",
    )
    parser.add_argument(
        "--connect-backoff-s",
        dest="connect_backoff_s",
        type=float,
        default=float(os.getenv("MCP_CONNECT_BACKOFF_S", "0.25")),
        help="Base backoff in seconds between session creation retries",
    )
    args = parser.parse_args()

    if args.port <= 0:
        raise ValueError("Port must be > 0")
    if args.max_workers <= 0:
        raise ValueError("max-workers must be > 0")
    if args.connect_retries < 0:
        raise ValueError("connect-retries must be >= 0")
    if args.connect_backoff_s < 0:
        raise ValueError("connect-backoff-s must be >= 0")

    return Settings(
        mode=args.mode,
        port=args.port,
        default_serial=args.default_serial,
        max_workers=args.max_workers,
        session_ttl_s=args.session_ttl_s,
        healthcheck_interval_s=args.healthcheck_interval_s,
        connect_retries=args.connect_retries,
        connect_backoff_s=args.connect_backoff_s,
    )
