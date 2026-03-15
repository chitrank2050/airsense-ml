#!/usr/bin/env python3
"""
scripts/menu.py — Polished interactive checkbox menu for ML-Notebook-Library.

Usage (via Makefile):
  uv run --with questionary scripts/menu.py [clean|obliviate|wizard]
"""

import subprocess
import sys
from pathlib import Path

try:
    import questionary
    from questionary import Choice
except ImportError:
    print("questionary not installed. Run: uv add questionary --dev")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# ── Polished style matching a modern dark-terminal look ──────────────────────
STYLE = questionary.Style(
    [
        ("qmark", "fg:#61dafb bold"),  # leading ? mark
        ("question", "fg:#ffffff bold"),  # prompt text
        ("answer", "fg:#61dafb bold"),  # confirmed answer
        ("pointer", "fg:#f0a500 bold"),  # ▶ cursor
        ("highlighted", "fg:#f0a500 bold"),  # row under cursor
        ("selected", "fg:#4ecca3"),  # ✔ ticked items
        ("separator", "fg:#555555 italic"),  # separator rows
        ("instruction", "fg:#555555"),  # keyboard hint line
    ]
)


# ── Helpers ──────────────────────────────────────────────────────────────────
def run_make(*targets: str) -> None:
    """Run one or more make targets, printing a warning if any fail."""
    for target in targets:
        result = subprocess.run(
            ["make", "--no-print-directory", target],
            cwd=ROOT,
        )
        if result.returncode != 0:
            print(f"\n  ⚠️  make {target!r} exited with code {result.returncode}\n")


# ── Execution order — never changes regardless of selection order ─────────────
EXECUTION_ORDER = [
    # Destructive first
    ("venv", lambda: run_make("_clean_venv")),
    ("cache", lambda: run_make("_clean_cache")),
    ("models", lambda: run_make("_clean_models")),
    ("mlflow_clean", lambda: run_make("_clean_mlflow")),
    ("logs", lambda: run_make("_clean_logs")),
    # Setup second
    ("init", lambda: run_make("init")),
    ("install", lambda: run_make("install")),
    # Pipeline third
    ("train", lambda: run_make("train")),
    ("tune", lambda: run_make("tune")),
    ("mlflow", lambda: run_make("mlflow")),
    ("api", lambda: run_make("api")),
    # Dev tools last
    ("lint", lambda: run_make("lint")),
    ("format", lambda: run_make("format")),
]


def execute_choices(choices: list[str]) -> None:
    """Execute selected actions in fixed dependency order, never user-selection order."""
    for key, fn in EXECUTION_ORDER:
        if key in choices:
            fn()


def _nothing_selected() -> None:
    print("\n  Nothing selected — no action taken.\n")


# ── Mode: make obliviate or clean ─────────────────────────────────────────────────────
def mode_obliviate() -> None:
    choices = questionary.checkbox(
        "🧹 Obliviate — select what to obliterate",
        choices=[
            Choice(
                "Cache files    (__pycache__, .pyc, dist, .ruff_cache…)", value="cache"
            ),
            Choice("Saved models   (models/)", value="models"),
            Choice("MLflow data    (mlruns.db, mlruns/)", value="mlflow_clean"),
            Choice("Logs           (logs/)", value="logs"),
            Choice("Virtual env    (.venv)", value="venv"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices)


# ── Entry point ──────────────────────────────────────────────────────────────
MODES = {
    "obliviate": mode_obliviate,
}

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "wizard"

    if mode not in MODES:
        print(f"Usage: {sys.argv[0]} [clean|obliviate|wizard]")
        sys.exit(1)

    try:
        MODES[mode]()
    except KeyboardInterrupt:
        print("\n\n  ✖ Cancelled — no action taken.\n")
        sys.exit(0)
