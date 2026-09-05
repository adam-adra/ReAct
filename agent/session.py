import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from agent.events import (
    Event,
    FinalAnswerEvent,
    ObservationEvent,
    ToolCallEvent,
    UserGoalEvent,
)


class Session:
    def __init__(self, session_id: Optional[str] = None):
        self.session_id: str = session_id or str(uuid.uuid4())[:8]
        self.created_at: str = datetime.now(timezone.utc).isoformat()
        self.events: list[Event] = []

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def get_current_turn_history(self) -> list[str]:
        history: list[str] = []
        last_goal_idx = -1

        for i in range(len(self.events) - 1, -1, -1):
            if isinstance(self.events[i], UserGoalEvent):
                last_goal_idx = i
                break

        if last_goal_idx == -1:
            return history

        turn_events = self.events[last_goal_idx + 1:]
        step_tools: dict[int, ToolCallEvent] = {}
        step_observations: dict[int, ObservationEvent] = {}

        for ev in turn_events:
            if isinstance(ev, ToolCallEvent):
                step_tools[ev.step] = ev
            elif isinstance(ev, ObservationEvent):
                step_observations[ev.step] = ev

        for step in sorted(step_tools.keys()):
            tool_ev = step_tools[step]
            obs_ev = step_observations.get(step)
            res_str = ""
            if obs_ev is not None:
                res_str = str(obs_ev.result)
                if len(res_str) > 300:
                    res_str = res_str[:300] + "... [truncated]"

            record = f"Step {step}: Called {tool_ev.tool}({tool_ev.arguments})"
            if res_str:
                record += f" -> Result: {res_str}"
            history.append(record)

        return history

    def get_past_turns_summary(self, max_turns: int = 3) -> str:
        turns: list[dict[str, str]] = []
        current_user_goal: Optional[str] = None
        current_final_answer: Optional[str] = None

        for ev in self.events:
            if isinstance(ev, UserGoalEvent):
                if current_user_goal is not None and current_final_answer is not None:
                    turns.append(
                        {"goal": current_user_goal, "answer": current_final_answer}
                    )
                current_user_goal = ev.goal
                current_final_answer = None
            elif isinstance(ev, FinalAnswerEvent):
                current_final_answer = ev.answer

        if current_user_goal is not None and current_final_answer is not None:
            turns.append({"goal": current_user_goal, "answer": current_final_answer})

        past_turns = turns[:-1] if len(turns) > 1 else []
        if not past_turns:
            return ""

        recent_turns = past_turns[-max_turns:]
        summary_lines: list[str] = []
        for turn in recent_turns:
            ans = turn["answer"].strip().replace("\n", " ")
            if len(ans) > 150:
                ans = ans[:150] + "..."
            summary_lines.append(f"- User: {turn['goal']}\n  Agent: {ans}")

        return "\n".join(summary_lines)

    def save_to_disk(self, directory: str = "sessions") -> str:
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"session_{self.session_id}.json")
        data: dict[str, Any] = {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "event_count": len(self.events),
            "events": [ev.model_dump() for ev in self.events],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    @classmethod
    def load_from_disk(cls, filepath: str) -> "Session":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        session = cls(session_id=data.get("session_id"))
        session.created_at = data.get("created_at", session.created_at)

        for ev_dict in data.get("events", []):
            ev_type = ev_dict.get("event_type")
            if ev_type == "user_goal":
                session.add_event(UserGoalEvent(**ev_dict))
            elif ev_type == "tool_call":
                session.add_event(ToolCallEvent(**ev_dict))
            elif ev_type == "observation":
                session.add_event(ObservationEvent(**ev_dict))
            elif ev_type == "final_answer":
                session.add_event(FinalAnswerEvent(**ev_dict))

        return session
