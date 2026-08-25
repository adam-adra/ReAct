from agent.agent import Agent
from agent.environment import Environment

# from agent.fake_decision import FakeDecisionMaker
from agent.qwen_decision import QwenDecisionMaker
from llm.qwen import Qwen
from tools.calculator import Calculator
from tools.registry import ToolRegistry
from tools.task import TaskManager

model = Qwen("models/qwen3-0.6b-q4_k_m.gguf")
registry = ToolRegistry()

registry.register(Calculator())
registry.register(TaskManager())

environment = Environment(registry)

decision_maker = QwenDecisionMaker(model)

agent = Agent(environment=environment, decision_maker=decision_maker)

result = agent.run("what is 7 * 7")

print("\nFINAL RESULT:")
print(result.get("answer"))
