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
    from questionary import Choice, Separator
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


def _clean_cache() -> None:
    run_make("_clean_cache")


def _clean_models() -> None:
    run_make("_clean_models")


def _clean_venv() -> None:
    run_make("_clean_venv")


def _nothing_selected() -> None:
    print("\n  Nothing selected — no action taken.\n")


# ── Mode: make clean ─────────────────────────────────────────────────────────
def mode_clean() -> None:
    choices = questionary.checkbox(
        "🧹  Clean — select what to remove",
        choices=[
            Choice(
                "Cache files    (__pycache__, .pyc, dist, .ruff_cache…)", value="cache"
            ),
            Choice("Saved models   (models/)", value="models"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    if "cache" in choices:
        _clean_cache()
    if "models" in choices:
        _clean_models()


# ── Mode: make obliviate ─────────────────────────────────────────────────────
def mode_obliviate() -> None:
    choices = questionary.checkbox(
        "☠️   Obliviate — select what to obliterate",
        choices=[
            Choice(
                "Cache files    (__pycache__, .pyc, dist, .ruff_cache…)", value="cache"
            ),
            Choice("Saved models   (models/)", value="models"),
            Choice("Virtual env    (.venv)", value="venv"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    # Always run in safe dependency order
    if "venv" in choices:
        _clean_venv()
    if "cache" in choices:
        _clean_cache()
    if "models" in choices:
        _clean_models()

    print()
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  To set up again:")
    print("  → Run 'make init'    to create venv")
    print("  → Run 'make install' to install deps")
    print("  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()


# ── Mode: make menu (full wizard) ────────────────────────────────────────────
def mode_wizard() -> None:
    choices = questionary.checkbox(
        "⚡  ML-Notebook-Library — what would you like to do?",
        choices=[
            Choice("Init     – Create virtual environment", value="init"),
            Choice("Install  – Sync dependencies", value="install"),
            Choice("Dev      – Launch Jupyter Lab", value="dev"),
            Choice("Lint     – Check code quality with ruff", value="lint"),
            Choice("Format   – Auto-format code with ruff", value="format"),
            Separator("── Cleanup ───────────────────────────────────"),
            Choice("Cache    – Remove __pycache__, dist, caches…", value="cache"),
            Choice("Models   – Remove saved models (models/)", value="models"),
            Choice("Venv     – Remove virtual environment (.venv)", value="venv"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    # Execute in dependency order: destructive first → setup → dev tools
    if "venv" in choices:
        _clean_venv()
    if "cache" in choices:
        _clean_cache()
    if "models" in choices:
        _clean_models()
    if "init" in choices:
        run_make("init")
    if "install" in choices:
        run_make("install")
    if "dev" in choices:
        run_make("dev")
    if "lint" in choices:
        run_make("lint")
    if "format" in choices:
        run_make("format")


# ── Entry point ──────────────────────────────────────────────────────────────
MODES = {
    "clean": mode_clean,
    "obliviate": mode_obliviate,
    "wizard": mode_wizard,
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
