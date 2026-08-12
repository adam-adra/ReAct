import json


def build_prompt(goal, observation, tools):
    tools_json = json.dumps(tools, indent=2)

    observation_json = json.dumps(observation, indent=2)

    return f"""You are an atonomous agent.
    Your job is to accomplish the user's goal by choosing actions.
    You have access to the following tools:
        {tools_json}
    Current goal:
        {goal}
    Current observation:
        {observation_json}
    You n=must respond with exacty one JSON object.
    If you need to use a tool:
    {{
        "type": "tool",
        "tool": "TOOL_NAME",
        "arguments": {{}}
    }}

    If the goal is complete:

    {{
        "type": "final",
        "answer": "FINAL ANSWER"
    }}

    Do not output anything outside the JSON object."""
