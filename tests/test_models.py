"""Tests for FakeModel and FakeModelProvider."""

import pytest
from agents import Agent, RunConfig, Runner

from openai_agents_testkit import FakeModel, FakeModelProvider


class TestFakeModel:
    """Tests for FakeModel."""

    @pytest.mark.asyncio
    async def test_get_response_returns_model_response(self):
        """Test that get_response returns a valid ModelResponse."""
        model = FakeModel(delay=0)

        response = await model.get_response(
            system_instructions="Test instructions",
            input="Hello",
            model_settings=None,
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=None,
        )

        assert response.output is not None
        assert len(response.output) == 1
        assert response.usage.total_tokens == 150

    @pytest.mark.asyncio
    async def test_call_count_increments(self):
        """Test that call_count increments with each call."""
        model = FakeModel(delay=0)

        assert model.call_count == 0

        await model.get_response(
            system_instructions=None,
            input="First",
            model_settings=None,
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=None,
        )
        assert model.call_count == 1

        await model.get_response(
            system_instructions=None,
            input="Second",
            model_settings=None,
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=None,
        )
        assert model.call_count == 2

    @pytest.mark.asyncio
    async def test_call_history_records_details(self):
        """Test that call_history records call details."""
        model = FakeModel(delay=0)

        await model.get_response(
            system_instructions="Be helpful",
            input="Test input",
            model_settings=None,
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=None,
        )

        assert len(model.call_history) == 1
        assert model.call_history[0]["system_instructions"] == "Be helpful"
        assert model.call_history[0]["input"] == "Test input"

    @pytest.mark.asyncio
    async def test_custom_response_factory(self):
        """Test that custom response_factory is used."""

        def custom_factory(call_id, input):
            return f"Custom: {input}"

        model = FakeModel(delay=0, response_factory=custom_factory)

        response = await model.get_response(
            system_instructions=None,
            input="Hello",
            model_settings=None,
            tools=[],
            output_schema=None,
            handoffs=[],
            tracing=None,
        )

        # Extract text from response
        text = response.output[0].content[0].text
        assert text == "Custom: Hello"

    def test_reset_clears_state(self):
        """Test that reset() clears call_count and call_history."""
        model = FakeModel(delay=0)
        model.call_count = 5
        model.call_history.append({"test": "data"})

        model.reset()

        assert model.call_count == 0
        assert len(model.call_history) == 0

    def test_stream_response_raises_not_implemented(self):
        """Test that stream_response raises NotImplementedError."""
        model = FakeModel()

        with pytest.raises(NotImplementedError, match="Streaming not implemented"):
            model.stream_response(
                system_instructions=None,
                input="Test",
                model_settings=None,
                tools=[],
                output_schema=None,
                handoffs=[],
                tracing=None,
            )


class TestFakeModelProvider:
    """Tests for FakeModelProvider."""

    def test_get_model_returns_fake_model(self):
        """Test that get_model returns a FakeModel instance."""
        provider = FakeModelProvider()

        model = provider.get_model("gpt-4")

        assert isinstance(model, FakeModel)

    def test_get_model_caches_by_name(self):
        """Test that get_model returns the same instance for same name."""
        provider = FakeModelProvider()

        model1 = provider.get_model("gpt-4")
        model2 = provider.get_model("gpt-4")
        model3 = provider.get_model("gpt-3.5-turbo")

        assert model1 is model2
        assert model1 is not model3

    def test_get_all_models(self):
        """Test that get_all_models returns all created models."""
        provider = FakeModelProvider()

        provider.get_model("model-a")
        provider.get_model("model-b")

        all_models = provider.get_all_models()

        assert len(all_models) == 2
        assert "model-a" in all_models
        assert "model-b" in all_models

    def test_clear_removes_all_models(self):
        """Test that clear() removes all cached models."""
        provider = FakeModelProvider()

        provider.get_model("test")
        assert len(provider.get_all_models()) == 1

        provider.clear()
        assert len(provider.get_all_models()) == 0

    def test_provider_passes_delay_to_models(self):
        """Test that provider delay is passed to created models."""
        provider = FakeModelProvider(delay=0.5)

        model = provider.get_model("test")

        assert model.delay == 0.5


class TestIntegration:
    """Integration tests with actual Agent and Runner."""

    def test_agent_with_fake_provider(self, fake_model_provider):
        """Test that agents work correctly with FakeModelProvider."""
        agent = Agent(
            name="Test Agent",
            model="gpt-4",
            instructions="You are a test agent.",
        )

        result = Runner.run_sync(
            agent,
            "Hello!",
            run_config=RunConfig(model_provider=fake_model_provider),
            max_turns=1,
        )

        assert result.final_output is not None
        assert "Fake response" in result.final_output

    def test_multiple_agents_share_provider(self, fake_model_provider):
        """Test that multiple agents can share the same provider."""
        agent1 = Agent(name="Agent 1", model="gpt-4", instructions="First")
        agent2 = Agent(name="Agent 2", model="gpt-4", instructions="Second")

        run_config = RunConfig(model_provider=fake_model_provider)

        Runner.run_sync(agent1, "Hello", run_config=run_config, max_turns=1)
        Runner.run_sync(agent2, "World", run_config=run_config, max_turns=1)

        # Both should use the same model instance
        model = fake_model_provider.get_model("gpt-4")
        assert model.call_count == 2
