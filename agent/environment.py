from tools.registry import ToolRegistry


class Environment:
    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry
        self.state = {"task_completed": False, "last_result": None}

    def execute(self, action: dict):
        tool_name = action["tool"]
        arguments = action["arguments"]

        try:
            tool = self.registry.get(tool_name)
            result = tool.execute(**arguments)
            self.state["last_result"] = result
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_state(self):
        return self.state

    def observe(self):
        return {
            "task_completed": self.state["task_completed"],
            "last_result": self.state["last_result"],
        }

    def get_tools(self):
        return self.registry.list_tools()

    def get_tool_schemas(self):
        return [tool.schema() for tool in self.registry.list_tools()]
