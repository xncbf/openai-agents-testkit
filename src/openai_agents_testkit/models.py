"""Fake models and providers for testing openai-agents-python."""

from __future__ import annotations

import asyncio
import uuid
from typing import TYPE_CHECKING, Any

from agents.items import ModelResponse, TResponseInputItem, TResponseStreamEvent
from agents.models.interface import Model, ModelProvider, ModelTracing
from agents.usage import Usage
from openai.types.responses import ResponseOutputMessage, ResponseOutputText

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    ResponseFactory = Callable[[int, str | list[TResponseInputItem]], str]


def default_response_factory(call_id: int, input_: str | list[TResponseInputItem]) -> str:
    """Default response factory that returns a simple message."""
    return f"Fake response #{call_id}"


class FakeModel(Model):
    """Fake model that returns predefined responses without calling any API.

    This model simulates API latency and returns configurable responses,
    making it ideal for testing agent behavior without actual API calls.

    Args:
        delay: Simulated response delay in seconds. Defaults to 0.1.
        response_factory: Optional callable that generates response text.
            Receives (call_id, input) and returns the response string.

    Example:
        >>> from openai_agents_testkit import FakeModel, FakeModelProvider
        >>> from agents import Agent, Runner, RunConfig
        >>>
        >>> provider = FakeModelProvider(delay=0.1)
        >>> agent = Agent(name="Test", model="fake-model", instructions="Test")
        >>> result = Runner.run_sync(
        ...     agent,
        ...     "Hello",
        ...     run_config=RunConfig(model_provider=provider),
        ... )
    """

    def __init__(
        self,
        delay: float = 0.1,
        response_factory: ResponseFactory | None = None,
    ) -> None:
        self.delay = delay
        self.response_factory = response_factory or default_response_factory
        self.call_count = 0
        self.call_history: list[dict[str, Any]] = []

    async def get_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: Any,
        tools: list[Any],
        output_schema: Any,
        handoffs: list[Any],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        prompt: Any = None,
    ) -> ModelResponse:
        """Return a fake response after simulated delay.

        Records call details in call_history for test assertions.
        """
        self.call_count += 1
        call_id = self.call_count

        # Record call for test assertions
        self.call_history.append(
            {
                "call_id": call_id,
                "system_instructions": system_instructions,
                "input": input,
                "tools": tools,
                "output_schema": output_schema,
            }
        )

        # Simulate async work / API latency
        if self.delay > 0:
            await asyncio.sleep(self.delay)

        # Generate response text
        response_text = self.response_factory(call_id, input)

        # Create proper OpenAI response types
        text_content = ResponseOutputText(
            type="output_text",
            text=response_text,
            annotations=[],
        )
        message = ResponseOutputMessage(
            id=f"msg-{uuid.uuid4().hex[:8]}",
            type="message",
            role="assistant",
            content=[text_content],
            status="completed",
        )

        return ModelResponse(
            output=[message],
            usage=Usage(requests=1, input_tokens=100, output_tokens=50, total_tokens=150),
            response_id=f"fake-response-{call_id}",
        )

    def stream_response(
        self,
        system_instructions: str | None,
        input: str | list[TResponseInputItem],
        model_settings: Any,
        tools: list[Any],
        output_schema: Any,
        handoffs: list[Any],
        tracing: ModelTracing,
        *,
        previous_response_id: str | None = None,
        conversation_id: str | None = None,
        prompt: Any = None,
    ) -> AsyncIterator[TResponseStreamEvent]:
        """Streaming is not implemented for FakeModel.

        Raises:
            NotImplementedError: Always raised as streaming is not supported.
        """
        raise NotImplementedError(
            "Streaming not implemented for FakeModel. Use FakeStreamingModel for streaming tests."
        )

    def reset(self) -> None:
        """Reset call count and history for clean test state."""
        self.call_count = 0
        self.call_history.clear()


class FakeModelProvider(ModelProvider):
    """Fake model provider that returns FakeModel instances.

    Manages a pool of FakeModel instances, one per model name,
    allowing consistent model access across multiple agent runs.

    Args:
        delay: Response delay for all models. Defaults to 0.1.
        response_factory: Optional response factory for all models.

    Example:
        >>> provider = FakeModelProvider(delay=0.5)
        >>> model = provider.get_model("gpt-4")
        >>> # Same instance returned for same model name
        >>> assert provider.get_model("gpt-4") is model
    """

    def __init__(
        self,
        delay: float = 0.1,
        response_factory: ResponseFactory | None = None,
    ) -> None:
        self.delay = delay
        self.response_factory = response_factory
        self._models: dict[str | None, FakeModel] = {}

    def get_model(self, model_name: str | None) -> Model:
        """Get or create a FakeModel for the given model name.

        Args:
            model_name: The model identifier (ignored, always returns FakeModel).

        Returns:
            A FakeModel instance, cached per model_name.
        """
        if model_name not in self._models:
            self._models[model_name] = FakeModel(
                delay=self.delay,
                response_factory=self.response_factory,
            )
        return self._models[model_name]

    def get_all_models(self) -> dict[str | None, FakeModel]:
        """Get all created model instances.

        Useful for inspecting call counts across all models in tests.
        """
        return self._models.copy()

    def reset_all(self) -> None:
        """Reset all model instances."""
        for model in self._models.values():
            model.reset()

    def clear(self) -> None:
        """Clear all cached model instances."""
        self._models.clear()
