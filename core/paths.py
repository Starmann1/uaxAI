"""Path helpers anchored to the installed project, not the process directory."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIRECTORY = PROJECT_ROOT / "config" / "industries"


def resolve_project_path(path: str | Path) -> Path:
    """Return an absolute project-root-relative path unless *path* is absolute."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else PROJECT_ROOT / candidate
