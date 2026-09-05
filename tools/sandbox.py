from pathlib import Path
import subprocess
from typing import Optional


class LocalSandbox:
    """
    Lightweight, pure-Python sandbox that confines execution to a root directory
    and persists working directory (cwd) state across steps without Docker.
    """

    def __init__(self, root_dir: Optional[str] = None, max_output_length: int = 2000) -> None:
        self.root = Path(root_dir or ".").resolve()
        self.cwd = self.root
        self.max_output_length = max_output_length

    def _normalize_command_paths(self, command: str) -> str:
        tokens = command.split()
        modified = False
        new_tokens = []
        for tok in tokens:
            if "/" in tok and not Path(tok).exists():
                fname = Path(tok).name
                if (self.cwd / fname).exists():
                    tok = fname
                    modified = True
                elif (self.cwd / f"_{fname}").exists():
                    tok = f"_{fname}"
                    modified = True
                else:
                    rel = tok.lstrip("/")
                    if (self.cwd / rel).exists():
                        tok = rel
                        modified = True
            elif not tok.startswith("-") and not (self.cwd / tok).exists():
                if (self.cwd / f"_{tok}").exists():
                    tok = f"_{tok}"
                    modified = True
            new_tokens.append(tok)
        return " ".join(new_tokens) if modified else command

    def execute(self, command: str, timeout: int = 15) -> tuple[int, str]:
        norm_command = self._normalize_command_paths(command)
        script = f"{norm_command}\n__ret=$?\npwd\nexit $__ret"

        try:
            res = subprocess.run(
                script,
                shell=True,
                executable="/bin/bash",
                cwd=self.cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return -1, f"Error: Command timed out after {timeout} seconds."
        except Exception as e:
            return -1, f"Error executing command: {e}"

        if res.returncode == 0:
            lines = res.stdout.rstrip().splitlines()
            output_lines = lines
            if lines:
                new_dir = Path(lines[-1]).resolve()
                if new_dir.is_relative_to(self.root):
                    self.cwd = new_dir
                    output_lines = lines[:-1]
                else:
                    self.cwd = self.root
                    output_lines = lines[:-1]

            output = "\n".join(output_lines).strip()
            if not output:
                output = "(Command executed successfully with no output)"
        else:
            err = res.stderr.strip() or res.stdout.strip()
            output = f"Command failed (exit code {res.returncode}):\n{err}"

        if len(output) > self.max_output_length:
            output = (
                output[: self.max_output_length]
                + f"\n[Warning: Output truncated at {self.max_output_length} characters]"
            )

        return res.returncode, output

    def get_relative_cwd(self) -> str:
        if self.cwd == self.root:
            return "."
        try:
            return str(self.cwd.relative_to(self.root))
        except ValueError:
            return "."
