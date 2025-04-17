from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from pathlib import Path
from llama_index.llms.openai import OpenAI

from aintellivr.utils.prompt_loader import load_prompt_library
from aintellivr.utils.structured_predict import run_structured_prediction
from aintellivr.utils.logging import logger
from aintellivr.utils.load_llm import get_llm
from aintellivr.utils.utils import RoutingConfiguration


class IntentClassification(BaseModel):
    """Structured output for intent classification"""

    classified_intent: str = Field(
        ..., description="The classified intent or 'needs_clarification'"
    )
    confidence_score: float = Field(
        ..., description="Confidence in the classification from 0.0 to 1.0"
    )
    is_emergency: bool = Field(
        ..., description="Whether emergency keywords were detected"
    )
    clarifying_questions: Optional[List[str]] = Field(
        None, description="List of clarifying questions if intent is unclear"
    )
    possible_intents: Optional[List[str]] = Field(
        None, description="List of possible intents when clarification is needed"
    )


class IntentRouter:
    def __init__(
        self,
        routing_config: RoutingConfiguration,
        prompts_dir: Path,
        llm: Optional[OpenAI] = None,
        llm_model: str = "gpt-4",
        temperature: float = 0.1,
    ):
        """
        Initialize the intent router.

        Args:
            routing_config: Configuration for routing rules
            prompts_dir: Directory containing prompt YAML files
            llm: Pre-loaded LLM instance (optional)
            llm_model: Model name to use if llm not provided
            temperature: Temperature setting if llm not provided
        """
        self.routing_config = routing_config
        self.prompt_library = load_prompt_library(prompts_dir)
        self.llm = (
            llm
            if llm is not None
            else get_llm(llm_model=llm_model, temperature=temperature)
        )

    def _format_intent_descriptions(self) -> str:
        """Format intent descriptions and examples for the prompt."""
        descriptions = []
        for rule in self.routing_config.routing_rules:
            desc = f"Intent: {rule['intent']}\n"
            desc += f"Description: {rule['description']}\n"
            desc += "Example utterances:\n"
            desc += "\n".join(f"- {ex}" for ex in rule["example_utterances"])
            descriptions.append(desc)
        return "\n\n".join(descriptions)

    async def classify_intent(self, user_input: str) -> IntentClassification:
        """Classify the user's intent using structured prediction."""
        prompt = self.prompt_library.get_prompt(
            "intent_routing", "intent_classification"
        )
        if not prompt:
            raise ValueError("Intent classification prompt not found")

        input_vars = {
            "user_input": user_input,
            "intent_descriptions": self._format_intent_descriptions(),
            "emergency_keywords": ", ".join(
                self.routing_config.get_emergency_keywords()
            ),
        }

        result = await run_structured_prediction(
            prompt=prompt,
            output_cls=IntentClassification,
            input_vars=input_vars,
            llm=self.llm,
        )

        return result

    async def process_user_input(self, user_input: str) -> Dict:
        """Process user input and return routing information."""
        try:
            classification = await self.classify_intent(user_input)

            if classification.is_emergency:
                return {
                    "status": "emergency",
                    "action": "route_to_emergency",
                    "classification": classification.dict(),
                }

            if classification.classified_intent == "needs_clarification":
                return {
                    "status": "needs_clarification",
                    "questions": classification.clarifying_questions,
                    "possible_intents": classification.possible_intents,
                    "classification": classification.dict(),
                }

            routing_rule = self.routing_config.get_routing_rule_by_intent(
                classification.classified_intent
            )

            if not routing_rule:
                return {
                    "status": "error",
                    "message": "No routing rule found for classified intent",
                    "classification": classification.dict(),
                }

            return {
                "status": "classified",
                "intent": classification.classified_intent,
                "confidence": classification.confidence_score,
                "route_to": routing_rule["route_to"],
                "required_prerequisites": routing_rule.get(
                    "required_prerequisites", []
                ),
                "optional_prerequisites": routing_rule.get(
                    "optional_prerequisites", []
                ),
                "classification": classification.dict(),
            }

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {"status": "error", "message": str(e)}
