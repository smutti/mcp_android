# MCP Android Server

Multi-device MCP server for Android automation, built in Python with `adbutils` and `uiautomator2`.

## What it does

- Exposes Android automation capabilities as MCP tools.
- Supports multiple connected devices in parallel.
- Uses per-device session caching and UI locks to avoid conflicting actions on the same device.
- Works with `stdio`, `streamable-http`, and `sse` transports.

## Tech stack

- Python `>=3.11`
- `uv` for dependency and environment management
- `mcp` (FastMCP)
- `adbutils`
- `uiautomator2`
- `Pillow`

## Prerequisites

- `adb` installed and available in `PATH`
- One or more Android devices/emulators connected and authorized (`adb devices`)
- `uv` installed

## Installation

```bash
uv sync
```

If you use an existing virtual environment:

```bash
source .venv/bin/activate
uv sync
```

## Run the server

### STDIO transport

```bash
uv run mcp-android-server --mode stdio
```

### Streamable HTTP transport

```bash
uv run mcp-android-server --mode streamable-http --port 3001
```

MCP endpoint URL:

```text
http://127.0.0.1:3001/mcp
```

### SSE transport

```bash
uv run mcp-android-server --mode sse --port 3001
```

## CLI options

```text
--mode {stdio,streamable-http,sse}
--port PORT
--default-serial SERIAL
--max-workers N
```

Environment variables (equivalent to CLI defaults):

- `MCP_TRANSPORT`
- `MCP_PORT`
- `MCP_DEFAULT_SERIAL`
- `MCP_MAX_WORKERS`

## MCP client configuration

### Codex over HTTP API

Add this to `~/.codex/config.toml`:

```toml
[mcp_servers.android]
url = "http://127.0.0.1:3001/mcp"
```

### Codex over local STDIO command

```toml
[mcp_servers.android]
command = "uv"
args = ["run", "mcp-android-server", "--mode", "stdio"]
cwd = "/absolute/path/to/mcp_android"

[mcp_servers.android.env]
PYTHONPATH = "src"
```

## Tool catalog

All device-specific tools accept `serial`.
If `serial` is omitted, resolution order is:

1. `--default-serial` / `MCP_DEFAULT_SERIAL`
2. The only connected device
3. Error if multiple devices are connected

### Device tools

- `list_devices()`
- `get_device_status(serial)`
- `clear_device_session(serial)`
- `list_active_sessions()`

### Logging

- `get_logcat_output(serial?, app_package, log_level="DEBUG", max_lines=100)`

`log_level` values:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`

### Screen and UI inspection

- `get_screenshot(serial?, scale_factor=0.4)`
- `get_ui_dump(serial?, returned_attributes)`

Allowed `returned_attributes` values:

- `index`, `text`, `resource-id`, `class`, `package`, `content-desc`
- `checkable`, `checked`, `clickable`, `enabled`, `focusable`, `focused`
- `scrollable`, `long-clickable`, `password`, `selected`, `bounds`
- `drawing-order`, `hint`

### UI interactions

- `click_ui_element(serial?, text?, resource_id?, content_desc?, timeout_s=10.0)`

For `click_ui_element`, provide exactly one selector among:

- `text`
- `resource_id`
- `content_desc`

### Input and system actions

- `tap_screen(serial?, x, y)`
- `swipe_screen(serial?, x1, y1, x2, y2, duration_ms=300)`
- `send_text(serial?, text_to_send, clear_existing=false)`
- `perform_system_action(serial?, action)` where `action` is:
  - `BACK`
  - `HOME`
  - `RECENT_APPS`

## Example flow

1. Call `list_devices`.
2. Call `get_screenshot` to inspect current state.
3. Call `get_ui_dump` to find selectors.
4. Call `click_ui_element` or `tap_screen`.
5. Call `get_logcat_output` for app diagnostics.

## Testing

Run unit tests:

```bash
uv run python -m unittest discover -s tests/unit -v
```

## Troubleshooting

- `Device not found`:
  - Check serial from `list_devices`.
- `Multiple devices connected. Please specify serial`:
  - Pass `serial` explicitly or set `--default-serial`.
- UI element not found:
  - Use `get_ui_dump` and verify the exact selector text/resource id/content description.
- No logs returned for `get_logcat_output`:
  - Ensure the app process is running and `app_package` is correct.
- ADB authorization issues:
  - Reconnect device and accept RSA authorization prompt.
