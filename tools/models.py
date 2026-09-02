from pydantic import BaseModel


class CalculatorArguments(BaseModel):
    a: float
    b: float


class TaskManagerArguments(BaseModel):
    completed: bool


class CreateFileArguments(BaseModel):
    file: str
    content: str
