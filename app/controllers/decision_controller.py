from typing import List
from app.data.repository import DataRepository
from app.models.criterion import Criterion
from app.models.alternative import Alternative
from app.services.decision_service import DecisionService
from app.services.visualization_service import VisualizationService


class DecisionController:
    def __init__(self) -> None:
        self.repo = DataRepository()
        self.decision_service = DecisionService()
        self.visualization_service = VisualizationService()

    def run(self) -> None:
        while True:
            print("\n=== Система підтримки прийняття рішень ===")
            print("1. Показати предметну область і дані")
            print("2. Додати критерій")
            print("3. Додати альтернативу")
            print("4. Побудувати рейтинг (Weighted Sum)")
            print("5. Побудувати рейтинг (TOPSIS)")
            print("6. Показати графік рейтингу")
            print("0. Вийти")

            choice = input("Оберіть дію: ").strip()

            if choice == "1":
                self.show_data()
            elif choice == "2":
                self.add_criterion()
            elif choice == "3":
                self.add_alternative()
            elif choice == "4":
                self.calculate_weighted_sum()
            elif choice == "5":
                self.calculate_topsis()
            elif choice == "6":
                self.show_chart()
            elif choice == "0":
                print("Завершення роботи.")
                break
            else:
                print("Невірний вибір.")

    def _load_models(self):
        data = self.repo.load()
        criteria = [Criterion(**c) for c in data["criteria"]]
        alternatives = [Alternative(**a) for a in data["alternatives"]]
        return data, criteria, alternatives

    def show_data(self) -> None:
        data, criteria, alternatives = self._load_models()
        print(f"\nПредметна область: {data.get('domain', 'Не вказано')}")
        print("\nКритерії:")
        for c in criteria:
            print(f"- {c.name}: вага={c.weight}, тип={c.criterion_type}")

        print("\nАльтернативи та матриця оцінювання:")
        for alt in alternatives:
            print(f"- {alt.name}: {alt.scores}")

    def add_criterion(self) -> None:
        data = self.repo.load()
        name = input("Назва критерію: ").strip()
        weight = float(input("Вага критерію: ").strip())
        criterion_type = input("Тип (maximize/minimize): ").strip()

        criterion = Criterion(name, weight, criterion_type)
        criterion.validate()

        data["criteria"].append({
            "name": criterion.name,
            "weight": criterion.weight,
            "criterion_type": criterion.criterion_type
        })
        self.repo.save(data)
        print("Критерій додано.")

    def add_alternative(self) -> None:
        data = self.repo.load()
        name = input("Назва альтернативи: ").strip()
        scores = {}

        for c in data["criteria"]:
            value = float(input(f"Оцінка для критерію '{c['name']}': ").strip())
            scores[c["name"]] = value

        data["alternatives"].append({
            "name": name,
            "scores": scores
        })
        self.repo.save(data)
        print("Альтернативу додано.")

    def calculate_weighted_sum(self) -> None:
        _, criteria, alternatives = self._load_models()
        ranking = self.decision_service.weighted_sum(criteria, alternatives)

        print("\nРейтинг альтернатив (Weighted Sum):")
        for i, (name, score) in enumerate(ranking, 1):
            print(f"{i}. {name} -> {score}")

        best_name = ranking[0][0]
        print("\nПояснення:")
        print(self.decision_service.explain_best(criteria, alternatives, best_name))

    def calculate_topsis(self) -> None:
        _, criteria, alternatives = self._load_models()
        ranking = self.decision_service.topsis(criteria, alternatives)

        print("\nРейтинг альтернатив (TOPSIS):")
        for i, (name, score) in enumerate(ranking, 1):
            print(f"{i}. {name} -> {score}")

    def show_chart(self) -> None:
        _, criteria, alternatives = self._load_models()
        ranking = self.decision_service.weighted_sum(criteria, alternatives)
        self.visualization_service.plot_ranking(ranking, "Рейтинг ноутбуків (Weighted Sum)")
