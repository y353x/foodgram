import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Скрипт импорта данных из JSON файла ингрединетов."""

    def handle(self, *args, **kwargs):
        self.import_ingredients()

    def import_ingredients(self):
        with open(
            './api/management/commands/ingredients.json',
            newline='', encoding='utf-8'
        ) as fixture:
            reader = json.load(fixture)
            for row in reader:
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
        self.stdout.write(
            self.style.SUCCESS('Данные успешно импортированы')
        )
