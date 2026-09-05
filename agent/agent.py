from agent.action import FinalAction
from agent.ui import AgentUI


class Agent:
    def __init__(self, environment, decision_maker):
        self.environment = environment
        self.decision_maker = decision_maker

    def run(self, goal: str, max_steps: int = 10):
        observation = self.environment.observe()
        history: list[str] = []

        for step in range(max_steps):
            step_num = step + 1

            action = self.decision_maker.decide(
                goal, observation, self.environment.get_tool_schemas(), history=history
            )

            if hasattr(action, "thought") and action.thought:
                AgentUI.thought(action.thought)

            if isinstance(action, FinalAction):
                AgentUI.final_answer(action.answer)
                return {
                    "status": "completed",
                    "answer": action.answer,
                    "thought": action.thought,
                    "steps": step_num,
                }

            AgentUI.tool_call(action.tool, action.arguments)

            observation = self.environment.execute(action.model_dump())
            AgentUI.observation(observation)

            res = observation.get("result", observation.get("message", "done"))
            history.append(
                f"Step {step_num}: Called {action.tool}({action.arguments}) -> Result: {res}"
            )

        err_msg = f"Agent exceeded maximum allowed steps ({max_steps})."
        AgentUI.error(err_msg)
        return {
            "status": "error",
            "message": err_msg,
        }
