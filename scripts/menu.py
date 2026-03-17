#!/usr/bin/env python3
"""
scripts/menu.py — Polished interactive checkbox menu for ML-Notebook-Library.

Usage (via Makefile):
  uv run --with questionary scripts/menu.py [clean|obliviate|wizard]
"""

import os
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


# ── Execution Orders — never change regardless of selection order ────────────
EXECUTION_ORDER_OBLIVIATE = [
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

EXECUTION_ORDER_DOCKER = [
    ("_docker-stop", lambda: run_make("_docker-stop")),
    ("_docker-clean", lambda: run_make("_docker-clean")),
    ("_docker-build", lambda: run_make("_docker-build")),
    ("_docker-run", lambda: run_make("_docker-run")),
    ("_docker-push", lambda: run_make("_docker-push")),
    ("_docker-deploy", lambda: run_make("_docker-deploy")),
    ("_docker-logs", lambda: run_make("_docker-logs")),
    ("_docker-shell", lambda: run_make("_docker-shell")),
]

EXECUTION_ORDER_AIRFLOW = [
    ("_airflow-down", lambda: run_make("_airflow-down")),
    ("_airflow-up", lambda: run_make("_airflow-up")),
    ("_airflow-logs", lambda: run_make("_airflow-logs")),
]

EXECUTION_ORDER_DOCS = [
    ("_docs-build", lambda: run_make("_docs-build")),
    ("_docs-deploy", lambda: run_make("_docs-deploy")),
    ("_docs", lambda: run_make("_docs")),
]

def _run_changelog_since() -> None:
    tag = questionary.text("Since tag (e.g. v0.1.0): ", style=STYLE).ask()
    if not tag:
        _nothing_selected()
        return
    print(f"📝 Changelog since {tag}...")
    subprocess.run(["uv", "run", "git-cliff", f"{tag}..HEAD", "--strip", "all"], cwd=ROOT)

EXECUTION_ORDER_GIT = [
    ("_changelog", lambda: run_make("_changelog")),
    ("_changelog-preview", lambda: run_make("_changelog-preview")),
    ("_changelog-since", _run_changelog_since),
    ("_git-tag", lambda: run_make("_git-tag")),
    ("_git-release", lambda: run_make("_git-release")),
]

def _run_db_migration() -> None:
    name = questionary.text("Migration name: ", style=STYLE).ask()
    if not name:
        _nothing_selected()
        return
    print(f"🗄️  Creating migration: {name}...")
    result = subprocess.run(
        ["uv", "run", "alembic", "revision", "--autogenerate", "-m", name],
        cwd=ROOT,
        env={**os.environ, "APP_ENV": "dev"},
    )
    if result.returncode == 0:
        print("✅ Migration created.")
    else:
        print(f"⚠️  Migration creation failed with code {result.returncode}.")

EXECUTION_ORDER_DB = [
    ("_db-rollback", lambda: run_make("_db-rollback")),
    ("_db-migration", _run_db_migration),
    ("_db-migrate", lambda: run_make("_db-migrate")),
]

from typing import Callable, Any

def execute_choices(choices: list[str], order_list: list[tuple[str, Any]]) -> None:
    """Execute selected actions in fixed dependency order, never user-selection order."""
    for key, fn in order_list:
        if key in choices:
            fn()


def _nothing_selected() -> None:
    print("\n  Nothing selected — no action taken.\n")


# ── Mode: obliviate ──────────────────────────────────────────────────────────
def mode_obliviate() -> None:
    choices = questionary.checkbox(
        "🧹 Obliviate — select what to obliterate",
        choices=[
            Choice("Cache files    (__pycache__, .pyc, dist, .ruff_cache…)", value="cache"),
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

    execute_choices(choices, EXECUTION_ORDER_OBLIVIATE)


# ── Mode: docker ─────────────────────────────────────────────────────────────
def mode_docker() -> None:
    choices = questionary.checkbox(
        "🐳 Docker — select actions",
        choices=[
            Choice("Build image", value="_docker-build"),
            Choice("Run container locally", value="_docker-run"),
            Choice("Stop container", value="_docker-stop"),
            Choice("Tail container logs", value="_docker-logs"),
            Choice("Shell into container", value="_docker-shell"),
            Choice("Push to Docker Hub", value="_docker-push"),
            Choice("Deploy (build + push)", value="_docker-deploy"),
            Choice("Clean Docker system", value="_docker-clean"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices, EXECUTION_ORDER_DOCKER)


# ── Mode: airflow ────────────────────────────────────────────────────────────
def mode_airflow() -> None:
    choices = questionary.checkbox(
        "🌬️ Airflow — select actions",
        choices=[
            Choice("Start Airflow cluster", value="_airflow-up"),
            Choice("Stop Airflow cluster", value="_airflow-down"),
            Choice("Tail Airflow logs", value="_airflow-logs"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices, EXECUTION_ORDER_AIRFLOW)


# ── Mode: docs ───────────────────────────────────────────────────────────────
def mode_docs() -> None:
    choices = questionary.checkbox(
        "📚 Docs — select actions",
        choices=[
            Choice("Start MkDocs dev server", value="_docs"),
            Choice("Build static site", value="_docs-build"),
            Choice("Deploy to GitHub Pages", value="_docs-deploy"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices, EXECUTION_ORDER_DOCS)


# ── Mode: git ────────────────────────────────────────────────────────────────
def mode_git() -> None:
    choices = questionary.checkbox(
        "🐙 Git — select actions",
        choices=[
            Choice("Generate CHANGELOG.md", value="_changelog"),
            Choice("Preview unreleased changes", value="_changelog-preview"),
            Choice("Preview changes since custom tag", value="_changelog-since"),
            Choice("Tag version from pyproject.toml", value="_git-tag"),
            Choice("Release (Tag + Changelog + GitHub release)", value="_git-release"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices, EXECUTION_ORDER_GIT)


# ── Mode: db ─────────────────────────────────────────────────────────────────
def mode_db() -> None:
    choices = questionary.checkbox(
        "🗄️ Database — select actions",
        choices=[
            Choice("Run database migrations", value="_db-migrate"),
            Choice("Create new migration", value="_db-migration"),
            Choice("Rollback last migration (-1)", value="_db-rollback"),
        ],
        style=STYLE,
    ).ask()

    if not choices:
        _nothing_selected()
        return

    execute_choices(choices, EXECUTION_ORDER_DB)


# ── Entry point ──────────────────────────────────────────────────────────────
MODES = {
    "obliviate": mode_obliviate,
    "docker": mode_docker,
    "airflow": mode_airflow,
    "docs": mode_docs,
    "git": mode_git,
    "db": mode_db,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in MODES:
        print(f"Usage: {sys.argv[0]} [{format('|'.join(MODES.keys()))}]")
        sys.exit(1)

    mode = sys.argv[1]

    try:
        MODES[mode]()
    except KeyboardInterrupt:
        print("\n\n  ✖ Cancelled — no action taken.\n")
        sys.exit(0)
