import yaml
from typing import Dict
from aintellivr.utils.logging import logger
from aintellivr.utils.directories import directories


def load_prompt_library() -> Dict[str, str]:
    """
    Load the prompt library from YAML files in the specified directory.
    """
    prompt_library = {}

    try:
        with open(directories.config_dir / "prompt_library.yaml", "r") as file:
            prompt_library = yaml.safe_load(file)
    except FileNotFoundError:
        logger.error("Prompt library file not found.")
    except yaml.YAMLError as e:
        logger.error(f"Error loading YAML file: {e}")

    return prompt_library


PROMPT_LIBRARY = load_prompt_library()
