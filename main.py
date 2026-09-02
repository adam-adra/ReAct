import _bootstrap  # noqa: F401

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from agent.agent import Agent
from agent.environment import Environment
from agent.qwen_decision import QwenDecisionMaker
from llm.qwen import Qwen
from tools.calculator import Calculator
from tools.file_creation import CreateFile
from tools.registry import ToolRegistry
from tools.task import TaskManager

console = Console()


def main():
    console.print(
        Panel.fit(
            "[bold cyan] AgentOS Interactive REPL[/bold cyan]\n"
            "[dim]Powered by local Qwen GGUF & Constrained JSON Decoding[/dim]\n"
            "[dim]Type your goal to run the agent, or 'exit' / 'quit' to stop.[/dim]",
            border_style="cyan",
        )
    )

    with console.status("[bold blue]Loading model and tools...[/bold blue]"):
        model = Qwen("models/qwen3-0.6b-q4_k_m.gguf")
        registry = ToolRegistry()
        registry.register(Calculator())
        registry.register(TaskManager())
        registry.register(CreateFile())
        environment = Environment(registry)
        decision_maker = QwenDecisionMaker(model)
        agent = Agent(environment=environment, decision_maker=decision_maker)

    console.print("[bold green]✓ Agent ready![/bold green]\n")

    while True:
        try:
            goal = Prompt.ask("[bold magenta]AgentOS[/bold magenta] »")
            if not goal.strip():
                continue

            if goal.strip().lower() in ("exit", "quit", "q"):
                console.print("[dim]Exiting AgentOS. Goodbye![/dim]")
                break

            environment.state = {"task_completed": False, "last_result": None}

            result = agent.run(goal)

            if result.get("status") == "completed":
                console.print(
                    Panel(
                        f"[bold green]{result.get('answer')}[/bold green]",
                        title="[bold green]Final Result[/bold green]",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"[bold red]{result.get('message')}[/bold red]",
                        title="[bold red]Error[/bold red]",
                        border_style="red",
                    )
                )
            console.print()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting AgentOS. Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()
