from agent.action import FinalAction


class Agent:
    def __init__(self, environment, decision_maker):
        self.environment = environment
        self.decision_maker = decision_maker

    def run(self, goal: str, max_steps: int = 10):
        observation = self.environment.observe()

        for step in range(max_steps):
            action = self.decision_maker.decide(
                goal, observation, self.environment.get_tool_schemas()
            )
            print(f"\nACTION (Step {step + 1}):")
            print(action)

            if isinstance(action, FinalAction):
                return {"status": "completed", "answer": action.answer}

            observation = self.environment.execute(action.model_dump())
            print("\nOBSERVATION:")
            print(observation)

        return {
            "status": "error",
            "message": f"Agent exceeded maximum allowed steps ({max_steps}).",
        }
