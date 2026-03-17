# Testing Suite

AirSense ML relies on `pytest` for unit and integration testing.

## Overview

We split tests logically into:
- `tests/api/`: Fast integration tests for all FastAPI endpoints. Ensures robust input validation and HTTP responses.
- `tests/data/`: Unit tests asserting data integrity and verifying that no target leakage occurs.

## Running Tests

To run the full test suite locally:

```bash
make test
```

To run a specific test file:

```bash
uv run pytest tests/api/test_predict.py
```

### Async Tests
Because the AirSense API uses `FastAPI` (which is async-native), the HTTP tests use `httpx.AsyncClient`. You'll notice they are decorated with `@pytest.mark.asyncio`.

## CI Integration
Tests are automatically run via GitHub Actions on every push to the `main` branch. See the [Continuous Integration](ci.md) page for details.
