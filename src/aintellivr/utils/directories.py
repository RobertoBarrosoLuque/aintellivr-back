import os
import pprint
from pathlib import Path
from typing import Union

from dotenv import load_dotenv

load_dotenv()


class _Directories:
    """
    Simple class to hold all important directories across
    repository. Allows to easily keep track of respective
    directories and refactor when necessary.
    """

    def __init__(self):
        self.home = Path(__file__).resolve().parents[4]
        self.root = Path(__file__).resolve().parents[3]
        self.cache_dir = self.root / "__cache__"
        self.data = self.home / "data"
        self.logs = self.home / "log"
        self.config_dir = self.home / "config"
        self.scripts = self.home / "scripts"


    def get_abs_path(self, base, path_parts: Union[str, list[str]]) -> str:
        if base not in self.__dict__:
            raise Exception(
                f"Base directory ({base}) is not defined in the _Directories class"
            )

        base_path = self.__dict__[base]

        if isinstance(path_parts, str):
            path_parts = [path_parts]
        return os.path.join(base_path, *[part.lstrip("/") for part in path_parts])

    def __repr__(self):
        return pprint.pformat(vars(self))


# Instantiate singleton directory instance
directories = _Directories()
