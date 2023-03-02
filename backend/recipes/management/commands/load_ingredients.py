import csv

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Loading ingradients data'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        with open(
            f'{data_path}/data/ingredients.csv',
            'r',
            encoding='utf-8'
        ) as file:
            reader = csv.reader(file)
            for row in reader:
                Ingredients.objects.create(
                    name=row[0], measurement_unit=row[1]
                )
        self.stdout.write(self.style.SUCCESS('Done!'))
