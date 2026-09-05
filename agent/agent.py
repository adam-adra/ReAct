from typing import Any, Optional

from agent.action import FinalAction
from agent.events import (
    FinalAnswerEvent,
    ObservationEvent,
    ToolCallEvent,
    UserGoalEvent,
)
from agent.session import Session
from agent.ui import AgentUI


class Agent:
    def __init__(
        self,
        environment: Any,
        decision_maker: Any,
        session: Optional[Session] = None,
    ) -> None:
        self.environment = environment
        self.decision_maker = decision_maker
        self.session = session or Session()

    def run(self, goal: str, max_steps: int = 10) -> dict[str, Any]:
        observation = self.environment.observe()

        self.session.add_event(UserGoalEvent(goal=goal))

        for step in range(max_steps):
            step_num = step + 1

            history = self.session.get_current_turn_history()

            action = self.decision_maker.decide(
                goal,
                observation,
                self.environment.get_tool_schemas(),
                history=history,
            )

            if hasattr(action, "thought") and action.thought:
                AgentUI.thought(action.thought)

            if isinstance(action, FinalAction):
                self.session.add_event(
                    FinalAnswerEvent(
                        step=step_num,
                        thought=action.thought,
                        answer=action.answer,
                    )
                )
                self.session.save_to_disk()
                AgentUI.final_answer(action.answer)
                return {
                    "status": "completed",
                    "answer": action.answer,
                    "thought": action.thought,
                    "steps": step_num,
                }

            self.session.add_event(
                ToolCallEvent(
                    step=step_num,
                    thought=action.thought,
                    tool=action.tool,
                    arguments=action.arguments,
                )
            )
            AgentUI.tool_call(action.tool, action.arguments)

            observation = self.environment.execute(action.model_dump())
            AgentUI.observation(observation)

            self.session.add_event(
                ObservationEvent(
                    step=step_num,
                    tool=action.tool,
                    status=observation.get("status", "unknown"),
                    result=observation.get("result", observation.get("message", "")),
                )
            )

        err_msg = f"Agent exceeded maximum allowed steps ({max_steps})."
        AgentUI.error(err_msg)
        self.session.save_to_disk()
        return {
            "status": "error",
            "message": err_msg,
        }
