from agent.environment import Environment
from tools.calculator import Calculator
from tools.registry import ToolRegistry
from tools.task import TaskManager

registry = ToolRegistry()

registry.register(Calculator())
registry.register(TaskManager())

environment = Environment(registry)

action = {"tool": "calculator", "arguments": {"a": 15, "b": 7}}

observation = environment.execute(action)

print(observation)
print(environment.get_tool_schemas())

print(environment.observe())
