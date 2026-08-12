from typing import Any

from tools.base import Tool
from tools.models import CalculatorArguments


class Calculator(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Multiplies two numbers"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number."},
                "b": {"type": "number", "description": "second number."},
            },
            "required": ["a", "b"],
        }

    @property
    def argument_model(self):
        return CalculatorArguments

    def execute(self, **kwargs: Any) -> float:
        validated = self.argument_model(**kwargs)
        return validated.a * validated.b
