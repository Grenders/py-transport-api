import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections["default"]
            except OperationalError:
                self.stdout.write("Database is not ready...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database is available"))
