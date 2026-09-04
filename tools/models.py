from pydantic import BaseModel


class BashArguments(BaseModel):
    command: str


class CalculatorArguments(BaseModel):
    a: float
    b: float


class TaskManagerArguments(BaseModel):
    completed: bool


class CreateFileArguments(BaseModel):
    file: str
    content: str


class ReadFileArguments(BaseModel):
    file: str
