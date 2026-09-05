import json
from typing import Optional

SYSTEM_PROMPT = """You are AgentOS, an autonomous local AI coding assistant.
Your job is to select the next JSON action to accomplish the user's goal.

RULES:
1. When a task requires inspecting files or running commands, select type="tool".
2. For greetings or conversation (such as "hi", "hello", "how are you"),
   select type="final" and reply helpfully without calling tools.
3. When EXECUTION HISTORY is present, the action has already finished.
   You are FORBIDDEN from calling any tool. You MUST select type="final" and
   provide the answer to the user's goal.
4. In the "thought" field, write 1 concise sentence describing your immediate step.
5. Output only valid JSON matching the schema.
"""


def build_user_prompt(
    goal: str,
    observation: dict,
    tools: list[dict],
    history: Optional[list[str]] = None,
) -> str:
    if history:
        history_lines = "\n".join(f"- {h}" for h in history)
        res = observation.get("result", observation.get("message", ""))
        return f"""GOAL: {goal}

EXECUTION HISTORY:
{history_lines}

OBSERVATION OUTPUT:
{res}

DECISION:
The command has already run. Do NOT call any tool again.
Select type="final" and answer the user's GOAL using the output above.
Action:"""

    tool_lines = [f"- {t['name']}: {t.get('description', '')}" for t in tools]
    tool_list = "\n".join(tool_lines)

    return f"""GOAL: {goal}

AVAILABLE TOOLS:
{tool_list}

CURRENT OBSERVATION:
{json.dumps(observation)}

DECISION:
If this is a greeting or does not require tools, select type="final".
Otherwise, select type="tool" and invoke the required tool.
Action:"""
