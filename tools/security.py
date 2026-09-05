import re
from typing import Optional


class SecurityGuard:
    FORBIDDEN_PATTERNS: list[tuple[re.Pattern[str], str]] = [
        (
            re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f?[a-zA-Z]*\s+)?/\s*($|\s|;)"),
            "Destructive command targeting root filesystem ('/') is blocked.",
        ),
        (
            re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+/\*"),
            "Destructive wildcard command targeting root filesystem ('/*') is blocked.",
        ),
        (
            re.compile(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*\s+~"),
            "Destructive command targeting user home directory ('~') is blocked.",
        ),
        (
            re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
            "Fork bomb pattern detected and blocked.",
        ),
        (
            re.compile(r"\bmkfs(\.[a-z0-9]+)?\b"),
            "Filesystem formatting command ('mkfs') is blocked.",
        ),
        (
            re.compile(r"\bdd\s+.*of=/dev/(sd[a-z]|nvme[0-9]|hd[a-z]|null|zero)"),
            "Direct raw disk write ('dd') is blocked.",
        ),
        (
            re.compile(r"\b(shutdown|reboot|poweroff|init\s+0|init\s+6)\b"),
            "System power control command is blocked.",
        ),
    ]

    @classmethod
    def validate(cls, command: str) -> tuple[bool, Optional[str]]:
        cmd = command.strip()
        for pattern, reason in cls.FORBIDDEN_PATTERNS:
            if pattern.search(cmd):
                return False, reason
        return True, None
