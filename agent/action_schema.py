from agent.action import FinalAction, ToolAction


def build_action_schema(tools: list[dict]) -> dict:
    tool_branches = []
    for tool in tools:
        tool_branches.append(
            {
                "type": "object",
                "properties": {
                    "type": {"const": "tool"},
                    "tool": {"const": tool["name"]},
                    "arguments": tool["parameters"],
                },
                "required": ["type", "tool", "arguments"],
                "additionalProperties": False,
            }
        )
    tool_branches.append(
        {
            "type": "object",
            "properties": {
                "type": {"const": "final"},
                "answer": {"type": "string"},
            },
            "required": ["type", "answer"],
            "additionalProperties": False,
        }
    )
    return {"oneOf": tool_branches}
