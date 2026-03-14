# Install pre-commit hook


## 1. Install ruff as dev dependency
```bash
uv add --dev ruff
```

## 2. Install pre-commit
```bash
uv add --dev pre-commit
```

## 3. Create .pre-commit-config.yaml
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.5
    hooks:
      - id: ruff
        args: [--fix]

      - id: ruff-format
```

## 4. Activate pre-commit hook
```bash
uv run pre-commit install
```

Now every git commit automatically runs Ruff.