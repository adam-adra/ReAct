from pathlib import Path
from typing import Any, Optional
from typing_extensions import override

from tools.base import Tool
from tools.models import CreateFileArguments
from tools.sandbox import LocalSandbox


class CreateFile(Tool):
    def __init__(self, sandbox: Optional[LocalSandbox] = None) -> None:
        self.sandbox = sandbox

    @property
    @override
    def name(self) -> str:
        return "create_file"

    @property
    @override
    def description(self) -> str:
        return (
            "Create or write a file with text content. "
            "Always use this tool when asked to create or write files."
        )

    @property
    @override
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "The name or path of the file to create"},
                "content": {
                    "type": "string",
                    "description": "The text content to write inside the file",
                },
            },
            "required": ["file", "content"],
        }

    @property
    @override
    def argument_model(self) -> Any:
        return CreateFileArguments

    def execute(self, **kwargs: Any) -> Any:
        validate = self.argument_model(**kwargs)
        try:
            target = Path(validate.file)
            if self.sandbox is not None and not target.is_absolute():
                target = self.sandbox.cwd / target
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(validate.content)
            return (
                f"The file '{validate.file}' was successfully created "
                f"with {len(validate.content)} characters."
            )
        except Exception as e:
            return f"Error while creating file: {e}"
