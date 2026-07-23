"""
Unix Executor — runs commands via subprocess (local) or SSH (remote).

For the demo: runs against the local machine.
For production: swap subprocess.run for paramiko SSH.
"""
import subprocess


class UnixExecutor:

    def run(self, command: str, timeout: int = 30) -> str:
        """
        Execute a shell command. Returns stdout or stderr string.
        Never raises — returns the error message as output so the agent can read it.
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout or result.stderr or "(no output)"
            return output.strip()
        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"Execution error: {e}"

    def verify_success(self, verify_output: str) -> bool:
        """
        Basic check: if the verify command returned non-empty output
        without common failure keywords, consider it a success.
        """
        failure_keywords = ["failed", "error", "not found", "inactive", "dead", "100%"]
        output_lower = verify_output.lower()
        return bool(verify_output.strip()) and not any(k in output_lower for k in failure_keywords)
