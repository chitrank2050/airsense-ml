# Pre-commit Hooks

AirSense ML uses pre-commit hooks to enforce code quality and conventional
commit messages on every commit automatically.

---

## Hooks Configured

| Hook | Purpose |
|---|---|
| `ruff` | Lint Python files, auto-fix where possible |
| `ruff-format` | Format Python files |
| `conventional-pre-commit` | Enforce conventional commit message format |

---

## Installation

### 1. Install dev dependencies
```bash
uv sync --all-groups
```

### 2. Install pre-commit hooks
```bash
uv run pre-commit install
```

### 3. Install commit-msg hook (conventional commits)
```bash
uv run pre-commit install --hook-type commit-msg
```

---

## Usage

Hooks run automatically on every `git commit`. No manual steps needed.

To run hooks manually against all files:
```bash
uv run pre-commit run --all-files
```

To update hook versions:
```bash
uv run pre-commit autoupdate
```

---

## Conventional Commit Format

All commit messages must follow this format:
```
<type>: <description>
```

**Allowed types:**

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Maintenance, dependency updates |
| `docs` | Documentation changes |
| `refactor` | Code restructuring, no behaviour change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system, Docker, Makefile changes |

**Examples:**
```
feat: add batch prediction endpoint
fix: resolve circular import in core.__init__
chore: update ruff to v0.15.6
docs: update development log phases
refactor: split feature_engineering into separate modules
build: optimise Docker image — strip nvidia packages
```

**Rejected examples:**
```
Update Makefile          ← no type prefix
fixed bug                ← no type prefix
WIP                      ← not descriptive
```

---

## Configuration

Hooks are defined in `.pre-commit-config.yaml` at project root:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.6
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v4.4.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]
        args: [feat, fix, chore, docs, refactor, perf, test, build]
```

---

## Skipping Hooks

For generated files like changelogs — skip pre-commit with `--no-verify`:
```bash
git commit --no-verify -m "docs: update changelog for v0.2.0"
```

Use sparingly. Never skip on feature commits.