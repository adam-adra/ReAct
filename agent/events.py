from datetime import datetime, timezone
from typing import Any, Literal
from pydantic import BaseModel, Field


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseEvent(BaseModel):
    timestamp: str = Field(default_factory=_utc_now_iso)
    event_type: str


class UserGoalEvent(BaseEvent):
    event_type: Literal["user_goal"] = "user_goal"
    goal: str


class ToolCallEvent(BaseEvent):
    event_type: Literal["tool_call"] = "tool_call"
    step: int
    thought: str
    tool: str
    arguments: dict[str, Any]


class ObservationEvent(BaseEvent):
    event_type: Literal["observation"] = "observation"
    step: int
    tool: str
    status: str
    result: Any


class FinalAnswerEvent(BaseEvent):
    event_type: Literal["final_answer"] = "final_answer"
    step: int
    thought: str
    answer: str


Event = UserGoalEvent | ToolCallEvent | ObservationEvent | FinalAnswerEvent
