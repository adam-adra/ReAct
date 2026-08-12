from agent.action import FinalAction, ToolAction


class Agent:
    def __init__(self, environment, decision_maker):
        self.environment = environment
        self.decision_maker = decision_maker

    def run(self, goal):

        observation = self.environment.observe()
        while True:
            action = self.decision_maker.decide(
                goal, observation, self.environment.get_tool_schemas()
            )
            print("\nACTION:")
            print(action)

            if isinstance(action, FinalAction):
                return {"status": "completed", "answer": action.answer}
            observation = self.environment.execute(action.model_dump())

            print("\n OBSERVATION:")
            print(observation)
