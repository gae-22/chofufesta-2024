import os
from typing import TypedDict
from logging import basicConfig, INFO

from dotenv import load_dotenv

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

load_dotenv()


class Config:
    TEST = False


class Member(TypedDict):
    mmaid: str
    called_by: str
    avatar_url: str


def setup_logging() -> None:
    basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")
