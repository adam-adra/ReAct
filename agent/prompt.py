import json
from typing import Optional

SYSTEM_PROMPT = """You are the decision-making engine of an autonomous AI agent.
Your job is to choose the next JSON action to accomplish the user goal.

RULES:
1. If the goal requires an action and it has not been completed yet, you MUST select type="tool".
2. If EXECUTION HISTORY shows the required action has already been performed successfully,
   you MUST select type="final" and summarize the completed answer.
3. NEVER call the same tool repeatedly if it has already succeeded!
4. NEVER write tool calls or fake code inside the "final" answer.
"""


def build_user_prompt(
    goal: str,
    observation: dict,
    tools: list[dict],
    history: Optional[list[str]] = None,
) -> str:
    tool_lines = [f"- {t['name']}: {t.get('description', '')}" for t in tools]
    tool_list = "\n".join(tool_lines)

    history_block = ""
    if history:
        history_lines = "\n".join(f"- {h}" for h in history)
        history_block = f"\nEXECUTION HISTORY:\n{history_lines}\n"

    decision_instruction = (
        "Review EXECUTION HISTORY. The action has already been executed successfully. "
        "Return type='final' with the final answer now."
        if history
        else "If the action has not been done yet, call the appropriate tool."
    )

    return f"""GOAL: {goal}

AVAILABLE TOOLS:
{tool_list}
{history_block}
CURRENT OBSERVATION:
{json.dumps(observation)}

DECISION:
{decision_instruction}
Action:"""
