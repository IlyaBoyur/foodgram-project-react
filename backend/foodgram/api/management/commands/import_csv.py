import csv

from tqdm import tqdm

import django.db.utils
from django.core.management.base import BaseCommand

from api.models import Ingredient

MESSAGE_START = 'Please wait until Finished! prompt'
MESSAGE_ERROR_CREATE = (
    'Unable to create {model} from {file} with values: {values}'
)
MESSAGE_SUCCESS_CREATE = 'Successfully created {total} {model} from {file}'
MESSAGE_FINISH = 'Finished!'

DATA = (
    ('../data/ingredients.csv', ('name', 'measurement_unit'), Ingredient),
)


class Command(BaseCommand):
    help = 'Imports data from csv files to database'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.NOTICE(MESSAGE_START)
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
                            MESSAGE_ERROR_CREATE.format(
                                model=Model.__name__,
                                file=file,
                                values=(*row.values(),)
                            )
                        ))
                        total -= 1
                self.stdout.write(self.style.SUCCESS(
                    MESSAGE_SUCCESS_CREATE.format(
                        total=total,
                        model=Model.__name__,
                        file=file,
                    )
                ))
        self.stdout.write(self.style.SUCCESS(MESSAGE_FINISH))
