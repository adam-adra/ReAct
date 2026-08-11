from tools.base import Tool


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

    def execute(self, completed: bool):
        return completed
