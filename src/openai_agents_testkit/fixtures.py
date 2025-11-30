"""Pytest fixtures for testing openai-agents-python applications.

This module provides pytest fixtures that are automatically available
when openai-agents-testkit is installed, thanks to the pytest11 entry point.

Usage:
    # In your test file, fixtures are auto-discovered
    def test_my_agent(fake_model_provider):
        agent = Agent(name="Test", model="gpt-4", instructions="Test")
        result = Runner.run_sync(
            agent,
            "Hello",
            run_config=RunConfig(model_provider=fake_model_provider),
        )
        assert "Fake response" in result.final_output
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from agents.tracing import set_tracing_disabled

from openai_agents_testkit.models import FakeModel, FakeModelProvider


def pytest_configure(config: pytest.Config) -> None:
    """Disable OpenAI agents tracing when testkit is loaded.

    Tracing is a separate telemetry subsystem that sends data to OpenAI's API.
    FakeModelProvider only mocks LLM API calls, not tracing calls.
    This hook ensures tracing is disabled before any tests run,
    preventing 401 errors from invalid API keys in test environments.
    """
    del config  # unused but required by pytest hook signature
    set_tracing_disabled(True)


if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from agents.items import TResponseInputItem

    ResponseFactory = Callable[[int, str | list[TResponseInputItem]], str]


@pytest.fixture
def fake_model() -> Generator[FakeModel, None, None]:
    """Provide a FakeModel instance for testing.

    The model is reset after each test to ensure clean state.

    Yields:
        A FakeModel instance with default settings (0.1s delay).

    Example:
        def test_model_calls(fake_model):
            # Use fake_model directly or via provider
            assert fake_model.call_count == 0
    """
    model = FakeModel(delay=0.1)
    yield model
    model.reset()


@pytest.fixture
def fake_model_provider() -> Generator[FakeModelProvider, None, None]:
    """Provide a FakeModelProvider instance for testing.

    All models are cleared after each test to ensure clean state.

    Yields:
        A FakeModelProvider instance with default settings.

    Example:
        def test_agent(fake_model_provider):
            agent = Agent(name="Test", model="gpt-4", instructions="Test")
            result = Runner.run_sync(
                agent,
                "Hello",
                run_config=RunConfig(model_provider=fake_model_provider),
            )
    """
    provider = FakeModelProvider(delay=0.1)
    yield provider
    provider.clear()


@pytest.fixture
def fake_model_provider_factory() -> Generator[Callable[..., FakeModelProvider], None, None]:
    """Factory fixture for creating customized FakeModelProvider instances.

    Use this when you need to customize delay or response_factory.

    Yields:
        A factory function that creates FakeModelProvider instances.

    Example:
        def test_slow_responses(fake_model_provider_factory):
            provider = fake_model_provider_factory(delay=2.0)
            # Test timeout handling...

        def test_custom_responses(fake_model_provider_factory):
            def custom_response(call_id, input):
                return f"Custom: {input}"
            provider = fake_model_provider_factory(response_factory=custom_response)
    """
    providers: list[FakeModelProvider] = []

    def factory(
        delay: float = 0.1,
        response_factory: ResponseFactory | None = None,
    ) -> FakeModelProvider:
        provider = FakeModelProvider(delay=delay, response_factory=response_factory)
        providers.append(provider)
        return provider

    yield factory

    # Cleanup all created providers
    for provider in providers:
        provider.clear()


@pytest.fixture
def no_delay_provider() -> Generator[FakeModelProvider, None, None]:
    """Provide a FakeModelProvider with zero delay for fast tests.

    Useful when you don't need to test timing behavior and want
    faster test execution.

    Yields:
        A FakeModelProvider with delay=0.
    """
    provider = FakeModelProvider(delay=0)
    yield provider
    provider.clear()
