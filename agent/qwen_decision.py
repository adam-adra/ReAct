import json

from agent.action import FinalAction, ToolAction
from agent.action_schema import ACTION_SCHEMA
from agent.decision import DecisionMaker
from agent.prompt import SYSTEM_PROMPT, build_user_prompt


class QwenDecisionMaker(DecisionMaker):
    def __init__(self, model) -> None:
        self.model = model

    def decide(self, goal, observation, tools):
        user_prompt = build_user_prompt(goal, observation, tools)

        response = self.model.generate(
            system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt, schema=ACTION_SCHEMA
        )
        data = json.loads(response)

        if data["type"] == "tool":
            return ToolAction(**data)
        if data["type"] == "final":
            return FinalAction(**data)

        raise ValueError(f"Unkown action type: {data['type']}")
