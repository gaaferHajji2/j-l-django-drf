from django.core.management.base import BaseCommand
from django.db import connection
from pathlib import Path
import os

class Command(BaseCommand):
    help = "seed the data for db"

    def handle(self, *args, **options) -> str | None:
        print("Begin seeding data")
        t1 = os.path.dirname(__file__)
        t2 = os.path.join(t1, 'seed.sql')
        t3 = Path(t2).read_text()

        with connection.cursor() as cursor:
            cursor.execute(t3)