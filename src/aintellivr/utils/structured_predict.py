from typing import Type, TypeVar, Dict, Any
from pydantic import BaseModel
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.openai import OpenAI
from aintellivr.utils.logging import logger

T = TypeVar("T", bound=BaseModel)


async def run_structured_prediction(
    prompt: PromptTemplate,
    output_cls: Type[T],
    input_vars: Dict[str, Any],
    llm: OpenAI,
) -> T:
    """
    Generic function to run structured prediction with a pre-loaded LLM.

    Args:
        prompt: The prompt template to use
        output_cls: Pydantic model class for output structure
        input_vars: Dictionary of input variables for the prompt
        llm: Pre-loaded LLM instance

    Returns:
        Instance of output_cls containing the structured prediction
    """
    try:
        result = await llm.astructured_predict(
            prompt=prompt, output_cls=output_cls, **input_vars
        )

        return result

    except Exception as e:
        logger.error(f"Error in structured prediction: {e}")
        raise
