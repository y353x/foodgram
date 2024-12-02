import json

from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.constants import PATH_TO_JSON
from foodgram_backend.settings import BASE_DIR
from recipes.models import Ingredient


class Command(BaseCommand):
    """Скрипт импорта данных из JSON файла ингрединетов."""

    def handle(self, *args, **kwargs):
        self.import_ingredients()

    def import_ingredients(self):
        with open(
            BASE_DIR / PATH_TO_JSON,
            newline='', encoding='utf-8'
        ) as fixture:
            reader = json.load(fixture)
            for row in tqdm(reader):
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
