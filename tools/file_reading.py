from typing import Any
from typing_extensions import override

from tools.base import Tool
from tools.models import ReadFileArguments


class ReadFile(Tool):
    @property
    @override
    def name(self) -> str:
        return "read_file"

    @property
    @override
    def description(self) -> str:
        return "Read the text content of an existing file in the working directory"

    @property
    @override
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The name or path of the file to read",
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
            with open(validate.file, "r", encoding="utf-8") as f:
                content = f.read(10000)
                if f.read(1):
                    return content + "\n[Warning: File content truncated at 10,000 characters]"
                return content
        except FileNotFoundError:
            return f"Error: File '{validate.file}' does not exist."
        except UnicodeDecodeError:
            return f"Error: File '{validate.file}' could not be decoded as UTF-8 text."
        except Exception as e:
            return f"Error while reading file: {e}"
