from __future__ import annotations
from typing import Dict, List, Tuple
from math import sqrt
from app.models.criterion import Criterion
from app.models.alternative import Alternative


class DecisionService:
    def normalize_weights(self, criteria: List[Criterion]) -> List[Criterion]:
        total = sum(c.weight for c in criteria)
        if total == 0:
            raise ValueError("Сума ваг критеріїв не може дорівнювати 0.")
        return [
            Criterion(c.name, c.weight / total, c.criterion_type)
            for c in criteria
        ]

    def weighted_sum(self, criteria: List[Criterion], alternatives: List[Alternative]) -> List[Tuple[str, float]]:
        criteria = self.normalize_weights(criteria)
        normalized_matrix = self._min_max_normalize(criteria, alternatives)

        results = []
        for alt in alternatives:
            total_score = 0.0
            for c in criteria:
                total_score += normalized_matrix[alt.name][c.name] * c.weight
            results.append((alt.name, round(total_score, 4)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def topsis(self, criteria: List[Criterion], alternatives: List[Alternative]) -> List[Tuple[str, float]]:
        criteria = self.normalize_weights(criteria)

        denominators: Dict[str, float] = {}
        for c in criteria:
            denominators[c.name] = sqrt(sum(alt.scores[c.name] ** 2 for alt in alternatives))

        weighted_matrix: Dict[str, Dict[str, float]] = {}
        for alt in alternatives:
            weighted_matrix[alt.name] = {}
            for c in criteria:
                value = alt.scores[c.name]
                denom = denominators[c.name] if denominators[c.name] != 0 else 1
                normalized = value / denom
                weighted_matrix[alt.name][c.name] = normalized * c.weight

        ideal_best: Dict[str, float] = {}
        ideal_worst: Dict[str, float] = {}

        for c in criteria:
            values = [weighted_matrix[alt.name][c.name] for alt in alternatives]
            if c.criterion_type == "maximize":
                ideal_best[c.name] = max(values)
                ideal_worst[c.name] = min(values)
            else:
                ideal_best[c.name] = min(values)
                ideal_worst[c.name] = max(values)

        results = []
        for alt in alternatives:
            d_best = sqrt(sum((weighted_matrix[alt.name][c.name] - ideal_best[c.name]) ** 2 for c in criteria))
            d_worst = sqrt(sum((weighted_matrix[alt.name][c.name] - ideal_worst[c.name]) ** 2 for c in criteria))
            closeness = d_worst / (d_best + d_worst) if (d_best + d_worst) != 0 else 0
            results.append((alt.name, round(closeness, 4)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def explain_best(self, criteria: List[Criterion], alternatives: List[Alternative], best_name: str) -> str:
        criteria = self.normalize_weights(criteria)
        normalized_matrix = self._min_max_normalize(criteria, alternatives)
        best = next(a for a in alternatives if a.name == best_name)

        contributions = []
        for c in criteria:
            contribution = normalized_matrix[best.name][c.name] * c.weight
            contributions.append((c.name, contribution, c.weight, best.scores[c.name], c.criterion_type))

        contributions.sort(key=lambda x: x[1], reverse=True)

        lines = [f"Найкраща альтернатива: {best.name}.",
                 "Основні причини вибору:"]
        for name, cont, weight, raw, ctype in contributions:
            lines.append(
                f"- {name}: значення = {raw}, тип = {ctype}, вага = {round(weight, 3)}, внесок = {round(cont, 4)}"
            )
        return "\n".join(lines)

    def _min_max_normalize(self, criteria: List[Criterion], alternatives: List[Alternative]) -> Dict[str, Dict[str, float]]:
        normalized: Dict[str, Dict[str, float]] = {}

        min_values = {}
        max_values = {}
        for c in criteria:
            values = [alt.scores[c.name] for alt in alternatives]
            min_values[c.name] = min(values)
            max_values[c.name] = max(values)

        for alt in alternatives:
            normalized[alt.name] = {}
            for c in criteria:
                current = alt.scores[c.name]
                min_v = min_values[c.name]
                max_v = max_values[c.name]

                if max_v == min_v:
                    normalized_value = 1.0
                else:
                    if c.criterion_type == "maximize":
                        normalized_value = (current - min_v) / (max_v - min_v)
                    else:
                        normalized_value = (max_v - current) / (max_v - min_v)

                normalized[alt.name][c.name] = normalized_value

        return normalized
