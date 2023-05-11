import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open("ingredients.csv", encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            Ingredient.objects.bulk_create([
                Ingredient(
                    id=number,
                    name=line[0],
                    measurement_unit=line[1]
                ) for number, line in enumerate(reader)
            ])
