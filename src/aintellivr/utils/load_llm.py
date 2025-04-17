import os

from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_llm(llm_model: str, temperature: float = 0.1) -> OpenAI:
    """
    Get the LLM instance based on the deployment group.

    Parameters
    ----------
    llm_model : str
        The model name.
    temperature : float
        The temperature value for the model.

    Returns
    -------
    LLM
        The LLM instance.
    """
    _api_key = os.getenv("OPENAI_API_KEY")
    if os.getenv("LLM_PROVIDER") == "fireworks":
        # Assuming you have a different initialization for the fireworks provider
        return OpenAI(
            model=llm_model,
            api_key=_api_key,
            api_base="https://api.fireworks.ai/inference/v1",
            temperature=temperature,
        )
    return OpenAI(model=llm_model, api_key=_api_key, temperature=temperature)
