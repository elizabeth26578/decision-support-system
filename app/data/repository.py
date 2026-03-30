import json
from pathlib import Path
from typing import Dict, Any


class DataRepository:
    def __init__(self, file_path: str = "data/sample_data.json") -> None:
        self.file_path = Path(file_path)

    def load(self) -> Dict[str, Any]:
        if not self.file_path.exists():
            return {"domain": "", "criteria": [], "alternatives": []}
        with self.file_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: Dict[str, Any]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with self.file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
