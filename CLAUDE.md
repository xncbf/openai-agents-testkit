# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

openai-agents-testkit is a testing utility library for [openai-agents-python](https://github.com/openai/openai-agents-python). It provides fake models, providers, and pytest fixtures for testing agent-based applications without making actual API calls.

## Project Structure

```
openai-agents-testkit/
├── src/openai_agents_testkit/
│   ├── __init__.py      # Public API exports
│   ├── models.py        # FakeModel, FakeModelProvider
│   ├── fixtures.py      # pytest fixtures (auto-discovered)
│   └── py.typed         # PEP 561 type marker
├── tests/
│   └── test_models.py   # Unit and integration tests
├── pyproject.toml       # Project config, dependencies
└── README.md
```

## Common Commands

```bash
# Install for development
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src/openai_agents_testkit --cov-report=term-missing

# Format code
ruff format .

# Lint code
ruff check .

# Fix lint issues
ruff check --fix .
```

## Key Design Decisions

1. **FakeModel implements `agents.models.interface.Model`** - This ensures compatibility with the openai-agents SDK's `RunConfig(model_provider=...)` pattern.

2. **FakeModelProvider caches models by name** - Same model name returns the same FakeModel instance, allowing call inspection across agent runs.

3. **Pytest fixtures via entry point** - The `pytest11` entry point in pyproject.toml makes fixtures auto-discoverable when the package is installed.

4. **Response factory pattern** - Allows users to customize responses without subclassing.

## Adding New Features

When adding new fake implementations:
1. Implement the corresponding interface from `agents.models.interface`
2. Add call tracking (call_count, call_history) for test assertions
3. Add a pytest fixture in `fixtures.py`
4. Export from `__init__.py`
5. Add tests in `tests/`
