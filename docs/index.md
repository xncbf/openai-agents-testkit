# openai-agents-testkit

Testing utilities for [openai-agents-python](https://github.com/openai/openai-agents-python): fake models, providers, and pytest fixtures.

## Installation

```bash
pip install openai-agents-testkit
```

## Quick Start

### Basic Usage

```python
from agents import Agent, Runner, RunConfig
from openai_agents_testkit import FakeModelProvider

provider = FakeModelProvider(delay=0.1)

agent = Agent(
    name="My Agent",
    model="gpt-4",
    instructions="You are a helpful assistant.",
)

result = Runner.run_sync(
    agent,
    "Hello!",
    run_config=RunConfig(model_provider=provider),
)

print(result.final_output)  # "Fake response #1"
```

### With pytest Fixtures

```python
from agents import Agent, Runner, RunConfig

def test_agent(fake_model_provider):
    agent = Agent(name="Test", model="gpt-4", instructions="Be helpful")

    result = Runner.run_sync(
        agent,
        "Hello",
        run_config=RunConfig(model_provider=fake_model_provider),
    )

    assert result.final_output is not None
```

## Features

- **FakeModel**: Returns predefined responses without API calls
- **FakeModelProvider**: Manages FakeModel instances
- **pytest fixtures**: Auto-discovered when installed
- **Call tracking**: Inspect model calls for assertions
