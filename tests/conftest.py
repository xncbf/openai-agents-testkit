"""Pytest configuration and fixtures."""

# Re-export fixtures from the package for local development
# (When installed, fixtures are auto-discovered via pytest11 entry point)
from openai_agents_testkit.fixtures import (
    fake_model,
    fake_model_provider,
    fake_model_provider_factory,
    no_delay_provider,
)

__all__ = [
    "fake_model",
    "fake_model_provider",
    "fake_model_provider_factory",
    "no_delay_provider",
]
