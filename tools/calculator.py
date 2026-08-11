from tools.base import Tool


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

    def execute(self, a: float, b: float) -> float:
        return a * b
