from typing import Any

from tools.base import Tool
from tools.models import TaskManagerArguments


class TaskManager(Tool):
    @property
    def name(self) -> str:
        return "task_manager"

    @property
    def description(self) -> str:
        return "Marks the current task as completed"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "completed": {
                    "type": "boolean",
                    "description": "whether is task completed.",
                }
            },
            "required": ["completed"],
        }

    @property
    def argument_model(self) -> Any:
        return TaskManagerArguments

    def execute(self, **kwargs: Any):
        validated = TaskManagerArguments(completed=kwargs["completed"])
        return validated.completed
