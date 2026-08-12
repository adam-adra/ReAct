from typing import Literal

from pydantic import BaseModel


class ToolAction(BaseModel):
    type: Literal["tool"]
    tool: str
    arguments: dict


class FinalAction(BaseModel):
    type: Literal["final"]
    answer: str
