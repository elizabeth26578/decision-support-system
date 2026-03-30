from dataclasses import dataclass


@dataclass
class Criterion:
    name: str
    weight: float
    criterion_type: str  # "maximize" or "minimize"

    def validate(self) -> None:
        if self.criterion_type not in ("maximize", "minimize"):
            raise ValueError(f"Невірний тип критерію: {self.criterion_type}")
        if self.weight < 0:
            raise ValueError("Вага критерію не може бути від'ємною.")
