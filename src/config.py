from os import getenv
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    load_dotenv()

    ADUANA_PY_BASE_URL: str = str(getenv("ADUANA_PY_BASE_URL", ""))
