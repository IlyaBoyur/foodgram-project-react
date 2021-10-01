import csv

import django.db.utils
from api.models import Ingredient
from django.core.management.base import BaseCommand
from tqdm import tqdm

DATA = (
    ('../data/ingredients.csv', ('name', 'measurement_unit'), Ingredient),
)


class Command(BaseCommand):
    help = 'Imports data from csv files to database'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE('Please wait until Finished! prompt')
        )
        for file, fieldnames, Model in DATA:
            with open(file, encoding='utf8') as csvfile:
                total = sum(1 for _ in csv.reader(csvfile))
                csvfile.seek(0)
                for row in tqdm(csv.DictReader(csvfile, fieldnames=fieldnames),
                                total=total):
                    try:
                        Model.objects.create(**row)
                    except django.db.utils.IntegrityError:
                        self.stdout.write(self.style.ERROR(
                            f'Unable to create {Model.__name__}'
                            f' from {file} with values: {*row.values(),}'
                        ))
                        total -= 1
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully created {total} {Model.__name__}'
                    f' from {file}'
                ))
        self.stdout.write(self.style.SUCCESS('Finished!'))
