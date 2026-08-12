import json

SYSTEM_PROMPT = """
    You are the decision-making compoenet of an autonomous agent.

    Your job is to choose the next action reqired to accomplish the user's goal.

    You have access to tools provided in the current context.

    choose exactly on action:
        1. Use a tool when additional work is required
        2. Return a final answer when the goal is complete.

    Do not explain your reasoning.
    Return only the structured action requested by the system.
"""


def build_user_prompt(goal, observation, tools):
    return f"""
   GOAL:
       {goal}

    AVAILABLE TOOLS:
        {json.dumps(tools, indent=2)}

    CURRENT OBSERVATION:
        {json.dumps(observation, indent=2)}
   """
