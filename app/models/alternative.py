from dataclasses import dataclass
from typing import Dict


@dataclass
class Alternative:
    name: str
    scores: Dict[str, float]
