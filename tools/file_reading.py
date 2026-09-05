from pathlib import Path
from typing import Any, Optional
from typing_extensions import override

from tools.base import Tool
from tools.models import ReadFileArguments
from tools.sandbox import LocalSandbox


class ReadFile(Tool):
    def __init__(self, sandbox: Optional[LocalSandbox] = None) -> None:
        self.sandbox = sandbox

    @property
    @override
    def name(self) -> str:
        return "read_file"

    @property
    @override
    def description(self) -> str:
        return "Read the text content of a specific file by name (e.g. 'main.py' or 'README.md')"

    @property
    @override
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The name or path of the file to read (e.g. 'main.py')",
                },
            },
            "required": ["file"],
        }

    @property
    @override
    def argument_model(self) -> Any:
        return ReadFileArguments

    def execute(self, **kwargs: Any) -> Any:
        validate = self.argument_model(**kwargs)
        try:
            target = Path(validate.file)
            if self.sandbox is not None:
                if not target.is_absolute():
                    target = self.sandbox.cwd / target
                else:
                    rel = str(validate.file).lstrip("/")
                    if (self.sandbox.cwd / rel).exists():
                        target = self.sandbox.cwd / rel

            if not target.exists():
                return f"Error: File '{validate.file}' does not exist."

            with open(target, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(1500)
                if f.read(1):
                    return content + "\n... [truncated at 1500 characters]"
                return content
        except Exception as e:
            return f"Error while reading file: {e}"
