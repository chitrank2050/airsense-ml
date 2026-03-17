# Continuous Integration (CI)

AirSense ML uses **GitHub Actions** for Continuous Integration (CI) to ensure code quality and consistency. The CI pipeline is completely **free** as it utilizes GitHub-provided runners.

## CI Workflow Overview

The CI pipeline runs automatically on:
- Every push to the `main` branch.
- Every Pull Request targeting the `main` branch.

### Jobs Executed

Currently, the `ci.yml` workflow performs the following tasks:

1. **Checkout Code**: Retrieves the latest codebase.
2. **Setup Environment**: Installs `uv` (our fast Python dependency manager) and sets up the correct Python version (read from `.python-version`).
3. **Install Dependencies**: Runs `uv sync` to install all required dependencies (using cached layers to speed up execution).
4. **Linting (`ruff`)**: Runs `uv run ruff check .` to find any coding errors or style violations. Unlike `make lint`, it runs in check-only mode and will fail the build if errors are detected.
5. **Formatting (`ruff`)**: Runs `uv run ruff format . --check` to ensure the code complies with our formatting standards. It will fail if any files require reformatting.

## Running Checks Locally

To avoid CI failures, you should run the checks locally before pushing your code. 

You can use the provided Make commands, which automatically apply fixes and formats:

```bash
# Automatically fix linting violations
make lint

# Automatically format the code
make format
```
