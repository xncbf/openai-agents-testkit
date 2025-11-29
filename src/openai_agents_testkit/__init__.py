"""Testing utilities for openai-agents-python.

This package provides fake models, providers, and pytest fixtures
for testing applications built with openai-agents-python.

Basic Usage:
    >>> from agents import Agent, Runner, RunConfig
    >>> from openai_agents_testkit import FakeModelProvider
    >>>
    >>> provider = FakeModelProvider(delay=0.1)
    >>> agent = Agent(name="Test", model="gpt-4", instructions="You are helpful.")
    >>> result = Runner.run_sync(
    ...     agent,
    ...     "Hello!",
    ...     run_config=RunConfig(model_provider=provider),
    ... )

With pytest fixtures (auto-discovered):
    # tests/test_my_agent.py
    def test_agent(fake_model_provider):
        agent = Agent(name="Test", model="gpt-4", instructions="Test")
        result = Runner.run_sync(
            agent,
            "Hello",
            run_config=RunConfig(model_provider=fake_model_provider),
        )
        assert result.final_output is not None
"""

from openai_agents_testkit.models import (
    FakeModel,
    FakeModelProvider,
    default_response_factory,
)

__all__ = [
    "FakeModel",
    "FakeModelProvider",
    "default_response_factory",
]

__version__ = "0.1.0"
