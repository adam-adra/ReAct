from agent.action import FinalAction, ToolAction

ACTION_SCHEMA = {
    "type": "object",
    "oneOf": [
        {
            "properties": {
                "type": {"const": "tool"},
                "tool": {"type": "string"},
                "arguments": {"type": "object"},
            },
            "required": ["type", "tool", "arguments"],
            "additionalProperties": False,
        },
        {
            "properties": {"type": {"const": "final"}, "answer": {"type": "string"}},
            "required": ["type", "answer"],
            "additionalProperties": False,
        },
    ],
}
