from agent.action import FinalAction, ToolAction
from agent.decision import DecisionMaker


class FakeDecisionMaker(DecisionMaker):
    def decide(self, goal, observation, tools, history=None):
        if observation.get("status") is None:
            return ToolAction(
                type="tool", tool="calculator", arguments={"a": 15, "b": 7}
            )
        return FinalAction(
            type="final",
            answer=f"The calculated result is {observation.get('result')}",
        )
