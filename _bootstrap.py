import sys
from pathlib import Path

# Automatically inject .venv site-packages if launched from external debugger / system python
_venv_site = (
    Path(__file__).parent
    / ".venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages"
)
if _venv_site.exists() and str(_venv_site.resolve()) not in sys.path:
    sys.path.insert(0, str(_venv_site.resolve()))
