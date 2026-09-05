import json
from typing import Optional

SYSTEM_PROMPT = """You are ReAct, an autonomous local AI coding assistant.
Your job is to select the next JSON action to accomplish the user's goal.

RULES:
1. To list files or see directory contents, select tool "execute_bash" with command "ls -A".
2. To check current directory path, select tool "execute_bash" with command "pwd".
3. To read, inspect, or show the content of a specific file, select tool "read_file".
4. To create or write a new file, select tool "create_file".
5. For greetings or conversation (such as "hi", "hello", "how are you"),
   select type="final" and reply helpfully without calling tools.
6. When tool execution results are present, select type="final".
7. In the "thought" field, write 1 concise sentence describing your immediate step.
8. Output only valid JSON matching the schema.
"""


def is_greeting(text: str) -> bool:
    cleaned = text.strip().lower().rstrip(".!?")
    greetings = {
        "hi",
        "hello",
        "hey",
        "greetings",
        "howdy",
        "how are you",
        "who are you",
        "what can you do",
        "help",
    }
    return cleaned in greetings


def build_user_prompt(
    goal: str,
    observation: dict,
    tools: list[dict],
    history: Optional[list[str]] = None,
) -> str:
    if is_greeting(goal):
        return f"""GOAL: {goal}

DECISION:
Reply politely and helpfully to the user. Select type="final".
Action:"""

    if history:
        history_lines = "\n".join(f"- {h}" for h in history)
        res = str(observation.get("result", observation.get("message", "")))
        if len(res) > 800:
            res = res[:800] + "\n... [truncated]"
        return f"""GOAL: {goal}

EXECUTION HISTORY:
{history_lines}

TOOL EXECUTION RESULT:
{res}

DECISION:
Answer the GOAL by summarizing the items in TOOL EXECUTION RESULT.
Select type="final".
Action:"""

    tool_lines = [f"- {t['name']}: {t.get('description', '')}" for t in tools]
    tool_list = "\n".join(tool_lines)

    return f"""GOAL: {goal}

AVAILABLE TOOLS:
{tool_list}

CURRENT OBSERVATION:
{json.dumps(observation)}

DECISION:
For conversational greetings (such as 'hi', 'hello'), select type="final".
For all queries and tasks (checking path, listing files, reading, creating), select type="tool".
Action:"""
