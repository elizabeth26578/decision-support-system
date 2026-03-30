import matplotlib.pyplot as plt
from typing import List, Tuple


class VisualizationService:
    def plot_ranking(self, ranking: List[Tuple[str, float]], title: str = "Рейтинг альтернатив") -> None:
        names = [item[0] for item in ranking]
        scores = [item[1] for item in ranking]

        plt.figure(figsize=(10, 6))
        plt.bar(names, scores)
        plt.title(title)
        plt.xlabel("Альтернативи")
        plt.ylabel("Інтегральна оцінка")
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.show()
