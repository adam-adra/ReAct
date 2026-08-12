import json

from agent.action import FinalAction, ToolAction
from agent.decision import DecisionMaker
from agent.prompt import build_prompt


class QwenDecisionMaker(DecisionMaker):
    def __init__(self, model) -> None:
        self.model = model

    def decide(self, goal, observation, tools):
        prompt = build_prompt(goal, observation, tools)

        response = self.model.generate(prompt)
        print(response)  ## we want to put gramatical constrained decoding
        data = json.loads(response)

        if data["type"] == "tool":
            return ToolAction(**data)
        if data["type"] == "final":
            return FinalAction(**data)
        raise ValueError(f"Unknown action type: {data['type']}")
