import os
from typing import Any, Callable, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

console = Console()
UIOutputCallback = Callable[[str], None]
_output_sink: Optional[UIOutputCallback] = None


def set_output_sink(sink: Optional[UIOutputCallback]) -> None:
    global _output_sink
    _output_sink = sink


def _emit(text: str) -> None:
    if _output_sink is not None:
        _output_sink(text)
    else:
        console.print(text)


class AgentUI:
    @staticmethod
    def banner(model_path: str, tool_names: list[str]) -> None:
        model_basename = os.path.basename(model_path)
        tool_str = ", ".join(f"[{t}]" for t in tool_names)

        banner_text = Text()
        banner_text.append("AgentOS", style="bold white")
        banner_text.append(" | Autonomous Coding Agent\n", style="cyan")
        banner_text.append(f"Model: {model_basename} (llama.cpp CPU)\n", style="dim")
        banner_text.append(f"Tools: {tool_str}", style="dim")

        if _output_sink is not None:
            _emit(f"[bold cyan]AgentOS[/bold cyan] | Model: {model_basename} | Tools: {tool_str}\n")
        else:
            console.print(
                Panel(
                    banner_text,
                    border_style="dim blue",
                    padding=(0, 2),
                )
            )

    @staticmethod
    def thought(thought: str) -> None:
        if not thought:
            return
        _emit(f"[dim italic]Thinking: {thought.strip()}[/dim italic]")

    @staticmethod
    def tool_call(tool: str, arguments: dict[str, Any]) -> None:
        if tool == "execute_bash":
            cmd = arguments.get("command", "")
            _emit(f"\n[bold yellow]$[/bold yellow] [bold white]{cmd}[/bold white]")
        else:
            args_str = ", ".join(f"{k}={v}" for k, v in arguments.items())
            _emit(f"\n[cyan]run {tool}[/cyan] [white]{args_str}[/white]")

    @staticmethod
    def observation(observation: dict[str, Any]) -> None:
        status = observation.get("status")
        if status == "success":
            result_str = str(observation.get("result", "")).strip()
            if result_str:
                lines = result_str.split("\n")
                if len(lines) > 30:
                    truncated = lines[:30]
                    displayed = "\n".join("  " + line for line in truncated)
                    displayed += f"\n  [dim]... ({len(lines) - 30} more lines truncated)[/dim]"
                else:
                    displayed = "\n".join("  " + line for line in lines)
                _emit(f"[dim]{displayed}[/dim]\n")
        else:
            err = observation.get("error", observation.get("message", "Unknown error"))
            _emit(f"  [red]Error: {err}[/red]\n")

    @staticmethod
    def final_answer(answer: str) -> None:
        if _output_sink is not None:
            _emit(f"\n{answer.strip()}\n")
        else:
            console.print()
            console.print(Markdown(answer.strip()))
            console.print()

    @staticmethod
    def error(message: str) -> None:
        _emit(f"\n[bold red]Error:[/bold red] {message}\n")
