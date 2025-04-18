import pytest
from llama_index.llms.openai import OpenAI

from aintellivr.utils.config_loaders import RoutingConfiguration, ROUTING_CONFIG
from aintellivr.utils.load_llm import get_llm
from aintellivr.modules.intent_router import IntentRouter


@pytest.fixture
def routing_config() -> RoutingConfiguration:
    """Load the routing configuration."""
    return ROUTING_CONFIG


@pytest.fixture
def llm() -> OpenAI:
    """Get the LLM instance."""
    return get_llm(llm_model="gpt-4", temperature=0.1)


@pytest.fixture
def intent_router(llm: OpenAI) -> IntentRouter:
    """Create an IntentRouter instance."""
    return IntentRouter(llm=llm)


@pytest.mark.asyncio
async def test_clear_intents(intent_router: IntentRouter):
    """Test cases with clear, unambiguous intents."""
    test_cases = [
        {
            "input": "I need to schedule a follow-up for my hip surgery",
            "expected_intent": "orthopedic_care",
            "expected_route": "orthopedics",
        },
        {
            "input": "I have a question about my hospital bill from last month",
            "expected_intent": "billing_inquiry",
            "expected_route": "billing",
        },
        {
            "input": "I'd like to become a new patient at your hospital",
            "expected_intent": "new_patient",
            "expected_route": "new_patients",
        },
    ]

    for case in test_cases:
        result = await intent_router.process_user_input(case["input"])
        assert result["status"] == "classified"
        assert result["intent"] == case["expected_intent"]
        assert result["route_to"] == case["expected_route"]
        assert result["confidence"] > 0.7


@pytest.mark.asyncio
async def test_emergency_cases(intent_router: IntentRouter):
    """Test emergency detection and handling."""
    test_cases = [
        "I'm having severe chest pain right now",
        "I can't breathe and my chest hurts",
        "My father is unconscious",
        "Having an emergency, severe chest pain",
    ]

    for input_text in test_cases:
        result = await intent_router.process_user_input(input_text)
        assert result["status"] == "emergency"
        assert result["action"] == "route_to_emergency"
        assert result["classification"]["is_emergency"] is True


@pytest.mark.asyncio
async def test_ambiguous_cases(intent_router: IntentRouter):
    """Test handling of ambiguous inputs that need clarification."""
    test_cases = [
        "I'm not feeling well",
        "I need to see a doctor",
        "Something's wrong with my stomach",
        "Need medical help",
    ]

    for input_text in test_cases:
        result = await intent_router.process_user_input(input_text)
        assert result["status"] == "needs_clarification"
        assert isinstance(result["questions"], list)
        assert len(result["questions"]) > 0
        assert isinstance(result["possible_intents"], list)
        assert len(result["possible_intents"]) > 0


@pytest.mark.asyncio
async def test_department_specific_routing(intent_router: IntentRouter):
    """Test routing to specific departments."""
    test_cases = [
        {
            "input": "My knee has been hurting for three weeks",
            "expected_department": "orthopedics",
        },
        {
            "input": "I need to discuss my blood pressure medication",
            "expected_department": "cardiovascular",
        },
        {
            "input": "I need to schedule a colonoscopy",
            "expected_department": "gastroenterology",
        },
    ]

    for case in test_cases:
        result = await intent_router.process_user_input(case["input"])
        assert result["status"] == "classified"
        assert result["route_to"] == case["expected_department"]


@pytest.mark.asyncio
async def test_prerequisites_included(intent_router: IntentRouter):
    """Test that prerequisites are included in the routing response."""
    input_text = "I need to schedule a follow-up for my hip surgery"
    result = await intent_router.process_user_input(input_text)

    assert "required_prerequisites" in result
    assert isinstance(result["required_prerequisites"], list)
    assert "optional_prerequisites" in result
    assert isinstance(result["optional_prerequisites"], list)


@pytest.mark.asyncio
async def test_confidence_scoring(intent_router: IntentRouter):
    """Test confidence score ranges and thresholds."""
    test_cases = [
        # Clear intent should have high confidence
        {"input": "I need to schedule a colonoscopy", "min_confidence": 0.8},
        # More ambiguous but still classifiable
        {
            "input": "Having some stomach issues and need to see someone",
            "min_confidence": 0.6,
        },
    ]

    for case in test_cases:
        result = await intent_router.process_user_input(case["input"])
        if result["status"] == "classified":
            assert result["confidence"] >= case["min_confidence"]


@pytest.mark.asyncio
async def test_error_handling(intent_router: IntentRouter):
    """Test error handling for edge cases."""
    test_cases = [
        "",  # Empty input
        "   ",  # Whitespace only
        "xyz" * 1000,  # Very long input
    ]

    for input_text in test_cases:
        result = await intent_router.process_user_input(input_text)
        assert "status" in result
        if result["status"] == "error":
            assert "message" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
