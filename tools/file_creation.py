from typing import Any
from typing_extensions import override

from tools.base import Tool
from tools.models import CreateFileArguments


class CreateFile(Tool):
    @property
    @override
    def name(self) -> str:
        return "create_file"

    @property
    @override
    def description(self) -> str:
        return "Create a new file in the working directory with the given content"

    @property
    @override
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "file": {"type": "string", "description": "The name or path of the file"},
                "content": {
                    "type": "string",
                    "description": "The text content to write to the file",
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
            with open(validate.file, "w") as f:
                f.write(validate.content)
                return f"The file '{validate.file}' was successfully created."
        except Exception as e:
            return f"Error while creating file: {e}"
