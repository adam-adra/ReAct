import json

from agent.action import FinalAction, ToolAction
from agent.action_schema import build_action_schema
from agent.decision import DecisionMaker
from agent.prompt import SYSTEM_PROMPT, build_user_prompt


class QwenDecisionMaker(DecisionMaker):
    def __init__(self, model) -> None:
        self.model = model

    def decide(self, goal, observation, tools, history=None):
        user_prompt = build_user_prompt(goal, observation, tools, history=history)

        action_schema = build_action_schema(tools)
        response = self.model.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema=action_schema,
        )
        print(response)
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            if '"answer":' in response:
                prefix = response.split('"answer":', 1)[1].strip()
                if prefix.startswith('"'):
                    prefix = prefix[1:]
                clean_answer = prefix.rstrip('"').rstrip("}").strip()
                data = {"type": "final", "answer": clean_answer}
            else:
                raise

        if data["type"] == "tool":
            print(data)
            return ToolAction(**data)
        if data["type"] == "final":
            return FinalAction(**data)

        raise ValueError(f"Unknown action type: {data['type']}")
