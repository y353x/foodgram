import json

from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.constants import PATH_TO_JSON
from recipes.models import Ingredient


class Command(BaseCommand):
    """Скрипт импорта данных из JSON файла ингрединетов."""

    def handle(self, *args, **kwargs):
        self.import_ingredients()

    def import_ingredients(self):
        path = settings.BASE_DIR / PATH_TO_JSON
        with open(
            path, newline='', encoding='utf-8'
        ) as fixture:
            reader = json.load(fixture)
            for row in tqdm(reader):
                Ingredient.objects.get_or_create(
                    name=row['name'],
                    measurement_unit=row['measurement_unit']
                )
        self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
