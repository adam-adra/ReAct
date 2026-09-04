import subprocess
from typing import Any
from typing_extensions import override

from tools.base import Tool
from tools.models import BashArguments


class ExecuteBash(Tool):
    @property
    @override
    def name(self) -> str:
        return "execute_bash"

    @property
    @override
    def description(self) -> str:
        return "Execute a bash shell command and return its stdout, stderr, and exit code"

    @property
    @override
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash shell command to execute",
                }
            },
            "required": ["command"],
        }

    @property
    @override
    def argument_model(self) -> Any:
        return BashArguments

    def execute(self, **kwargs: Any) -> Any:
        validate = self.argument_model(**kwargs)
        try:
            result = subprocess.run(
                validate.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if not output:
                    output = "(Command executed successfully with no output)"
                if len(output) > 2000:
                    return output[:2000] + "\n[Warning: Output truncated at 2000 characters]"
                return output
            else:
                stderr = result.stderr.strip() or result.stdout.strip()
                return f"Command failed (exit code {result.returncode}):\n{stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 15 seconds."
        except Exception as e:
            return f"Error executing bash command: {e}"
