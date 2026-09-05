import _bootstrap  # noqa: F401
import os
import sys
from typing import Optional

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Input, RichLog, Static

from agent.agent import Agent
from agent.environment import Environment
from agent.qwen_decision import QwenDecisionMaker
from agent.ui import set_output_sink
from llm.qwen import Qwen
from tools.bash import ExecuteBash
from tools.registry import ToolRegistry
from tools.sandbox import LocalSandbox


class AgentOSApp(App[None]):
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }

    #header-bar {
        dock: top;
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }

    #chat-log {
        height: 1fr;
        width: 100%;
        overflow-y: scroll;
        padding: 1 2;
        border-top: solid $primary;
        border-bottom: solid $primary;
        background: $surface-darken-1;
    }

    #input-container {
        dock: bottom;
        height: 3;
        width: 100%;
        background: $surface;
        padding: 0 1;
    }

    #user-input {
        width: 100%;
        border: tall $accent;
    }
    """

    def __init__(
        self,
        agent: Agent,
        environment: Environment,
        model_basename: str,
        sandbox: Optional[LocalSandbox] = None,
    ):
        super().__init__()
        self.agent = agent
        self.environment = environment
        self.model_basename = model_basename
        self.sandbox = sandbox

    def compose(self) -> ComposeResult:
        yield Static(
            f"AgentOS | Model: {self.model_basename} | Tool: [execute_bash]",
            id="header-bar",
        )
        yield RichLog(id="chat-log", markup=True, wrap=True)
        with Container(id="input-container"):
            yield Input(
                placeholder="AgentOS > Type your goal or command here... (or 'exit' to quit)",
                id="user-input",
            )

    def on_mount(self) -> None:
        log = self.query_one("#chat-log", RichLog)

        def textual_sink(text: str) -> None:
            self.call_from_thread(log.write, text)

        set_output_sink(textual_sink)

        log.write("[bold cyan]Welcome to AgentOS.[/bold cyan]")
        log.write(
            "[dim]The input prompt is anchored at the bottom. "
            "All thoughts, commands, and answers stream into the center window.[/dim]\n"
        )
        self.query_one("#user-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        goal = event.value.strip()
        if not goal:
            return

        inp = event.input
        inp.value = ""

        if goal.lower() in ("exit", "quit", "q"):
            self.exit()
            return

        log = self.query_one("#chat-log", RichLog)
        log.write(f"\n[bold white]> {goal}[/bold white]\n")

        inp.disabled = True
        self.run_agent_task(goal)

    @work(thread=True)
    def run_agent_task(self, goal: str) -> None:
        try:
            self.environment.state = {"task_completed": False, "last_result": None}
            self.agent.run(goal)
        except Exception as e:
            log = self.query_one("#chat-log", RichLog)
            self.call_from_thread(log.write, f"[bold red]Error: {e}[/bold red]\n")
        finally:
            inp = self.query_one("#user-input", Input)
            self.call_from_thread(setattr, inp, "disabled", False)
            self.call_from_thread(inp.focus)


def main() -> None:
    model_path = "models/qwen3-0.6b-q4_k_m.gguf"
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}. Run 'make download-model' first.")
        sys.exit(1)

    sandbox = LocalSandbox()
    model = Qwen(model_path)
    registry = ToolRegistry()
    registry.register(ExecuteBash(sandbox=sandbox))

    environment = Environment(registry)
    decision_maker = QwenDecisionMaker(model)
    agent = Agent(environment=environment, decision_maker=decision_maker)

    app = AgentOSApp(
        agent=agent,
        environment=environment,
        model_basename=os.path.basename(model_path),
        sandbox=sandbox,
    )
    app.run()


if __name__ == "__main__":
    main()
