def build_action_schema(
    tools: list[dict],
    include_tools: bool = True,
    include_final: bool = True,
) -> dict:
    tool_branches = []
    if include_tools:
        for tool in tools:
            tool_branches.append(
                {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": (
                                "Brief 1-2 sentence explanation of the next immediate step."
                            ),
                        },
                        "type": {"const": "tool"},
                        "tool": {"const": tool["name"]},
                        "arguments": tool["parameters"],
                    },
                    "required": ["type", "tool", "arguments", "thought"],
                    "additionalProperties": False,
                }
            )

    if include_final:
        tool_branches.append(
            {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": (
                            "Brief 1-2 sentence explanation of the next immediate step."
                        ),
                    },
                    "type": {"const": "final"},
                    "answer": {"type": "string"},
                },
                "required": ["type", "answer", "thought"],
                "additionalProperties": False,
            }
        )
    return {"oneOf": tool_branches}
