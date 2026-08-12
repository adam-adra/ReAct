from agent.decision import DecisionMaker


class FakeDecisionMaker(DecisionMaker):
    def decide(self, goal, observation, tool):
        if observation.get("status") is None:
            return {"tool": "calculator", "arguments": {"a": 15, "b": 7}}
        return {"tool": "task_manager", "arguments": {"completed": True}}
