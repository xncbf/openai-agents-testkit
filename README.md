# openai-agents-testkit

[![PyPI version](https://badge.fury.io/py/openai-agents-testkit.svg)](https://badge.fury.io/py/openai-agents-testkit)
[![Python Versions](https://img.shields.io/pypi/pyversions/openai-agents-testkit.svg)](https://pypi.org/project/openai-agents-testkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Testing utilities for [openai-agents-python](https://github.com/openai/openai-agents-python): fake models, providers, and pytest fixtures.

> **Note**: This is an unofficial community library, not affiliated with OpenAI.

## Installation

```bash
pip install openai-agents-testkit
```

## Quick Start

### Basic Usage

```python
from agents import Agent, Runner, RunConfig
from openai_agents_testkit import FakeModelProvider

# Create a fake provider (no API calls!)
provider = FakeModelProvider(delay=0.1)

# Use it with any agent
agent = Agent(
    name="My Agent",
    model="gpt-4",  # Model name is ignored, FakeModel is always used
    instructions="You are a helpful assistant.",
)

result = Runner.run_sync(
    agent,
    "Hello, how are you?",
    run_config=RunConfig(model_provider=provider),
)

print(result.final_output)  # "Fake response #1"
```

### With pytest Fixtures

Fixtures are auto-discovered when you install the package:

```python
# tests/test_my_agent.py
from agents import Agent, Runner, RunConfig

def test_agent_responds(fake_model_provider):
    """fake_model_provider is automatically available!"""
    agent = Agent(name="Test", model="gpt-4", instructions="Be helpful")

    result = Runner.run_sync(
        agent,
        "Hello",
        run_config=RunConfig(model_provider=fake_model_provider),
    )

    assert result.final_output is not None
    assert "Fake response" in result.final_output
```

### Custom Responses

```python
from openai_agents_testkit import FakeModelProvider

def my_response_factory(call_id: int, input) -> str:
    """Generate custom responses based on input."""
    if "hello" in str(input).lower():
        return "Hi there!"
    return f"Response #{call_id}: I processed your request."

provider = FakeModelProvider(
    delay=0.0,  # No delay for fast tests
    response_factory=my_response_factory,
)
```

### Inspecting Calls

```python
def test_agent_tool_usage(fake_model_provider):
    agent = Agent(name="Test", model="gpt-4", instructions="Test")

    Runner.run_sync(
        agent,
        "Do something",
        run_config=RunConfig(model_provider=fake_model_provider),
    )

    # Get the model instance
    model = fake_model_provider.get_model("gpt-4")

    # Inspect call history
    assert model.call_count == 1
    assert model.call_history[0]["system_instructions"] == "Test"
```

## Available Fixtures

| Fixture | Description |
|---------|-------------|
| `fake_model` | A single `FakeModel` instance |
| `fake_model_provider` | A `FakeModelProvider` with 0.1s delay |
| `fake_model_provider_factory` | Factory for custom provider configuration |
| `no_delay_provider` | A `FakeModelProvider` with zero delay |

## API Reference

### FakeModel

```python
FakeModel(
    delay: float = 0.1,  # Simulated API latency
    response_factory: Callable[[int, input], str] | None = None,
)
```

**Attributes:**
- `call_count: int` - Number of times the model was called
- `call_history: list[dict]` - Details of each call

**Methods:**
- `reset()` - Reset call count and history

### FakeModelProvider

```python
FakeModelProvider(
    delay: float = 0.1,
    response_factory: Callable[[int, input], str] | None = None,
)
```

**Methods:**
- `get_model(model_name)` - Get/create a FakeModel for the name
- `get_all_models()` - Get all created model instances
- `reset_all()` - Reset all model instances
- `clear()` - Clear all cached models

## Use Cases

- **Unit testing agents** without API costs
- **Integration testing** agent workflows
- **CI/CD pipelines** that can't access OpenAI API
- **Development** when iterating on agent logic
- **Concurrent testing** (FakeModel is thread-safe)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.
