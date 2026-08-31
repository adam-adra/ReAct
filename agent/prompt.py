import json

SYSTEM_PROMPT = """You are the decision-making component of an autonomous AI agent.
Your job is to choose the next action to accomplish the user's goal.

Rules:
1. If the CURRENT OBSERVATION already contains the result needed for the goal,
   return a "final" action with the answer string.
2. If you need to perform a calculation or action, choose the appropriate tool.
3. Do not call a tool repeatedly if the result is already in the observation.
4. Return only the structured JSON action requested.
"""


def build_user_prompt(goal, observation, tools):
    return f"""GOAL:
{goal}

AVAILABLE TOOLS:
{json.dumps(tools, indent=2)}

CURRENT OBSERVATION:
{json.dumps(observation, indent=2)}

DECISION INSTRUCTION:
Review the CURRENT OBSERVATION. If it already contains the calculation or result
to satisfy the GOAL, return type "final" with the answer string.
Otherwise, invoke the required tool."""
