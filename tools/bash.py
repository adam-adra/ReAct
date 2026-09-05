from typing import Any, Optional
from typing_extensions import override

from tools.base import Tool
from tools.models import BashArguments
from tools.sandbox import LocalSandbox
from tools.security import SecurityGuard


class ExecuteBash(Tool):
    def __init__(self, sandbox: Optional[LocalSandbox] = None) -> None:
        self.sandbox = sandbox or LocalSandbox()

    @property
    @override
    def name(self) -> str:
        return "execute_bash"

    @property
    @override
    def description(self) -> str:
        return (
            "Execute a bash shell command (e.g. 'cat <file>' to view file contents, "
            "'ls' to list files) and return its stdout, stderr, and exit code"
        )

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

        is_safe, reason = SecurityGuard.validate(validate.command)
        if not is_safe:
            return f"Security Violation: {reason}"

        _, output = self.sandbox.execute(validate.command, timeout=15)
        return output
