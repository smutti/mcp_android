class ShellService:
    """Provides shell command execution on a target device."""

    @staticmethod
    def run(device, command: str) -> str:
        output = device.shell(command)
        return str(output)
