"""
Windows Executor — stub for the demo.
Returns realistic mock output so the Windows Agent functions in demos.
In production: wire to WinRM (pywinrm) or PowerShell remoting.
"""


class WindowsExecutor:

    _MOCK_OUTPUTS = {
        "disk": "C: Used=45GB Free=55GB\nD: Used=10GB Free=90GB",
        "services": "DNS Client  Stopped  Automatic",
        "event_log": "EventID 7036: DNS Client service stopped.",
        "default": "Command executed successfully (mock).",
    }

    def run(self, command: str, timeout: int = 30) -> str:
        """Returns mock output for the demo."""
        command_lower = command.lower()
        if "psdrive" in command_lower or "disk" in command_lower:
            return self._MOCK_OUTPUTS["disk"]
        if "get-service" in command_lower or "service" in command_lower:
            return self._MOCK_OUTPUTS["services"]
        if "get-eventlog" in command_lower or "event" in command_lower:
            return self._MOCK_OUTPUTS["event_log"]
        return self._MOCK_OUTPUTS["default"]

    def verify_success(self, verify_output: str) -> bool:
        return "successfully" in verify_output.lower() or bool(verify_output.strip())
