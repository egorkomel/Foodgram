import csv
import json
import os

from api.models import Ingredient
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Read from db or write from json/csv to db.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--read',
            action='store_true',
            help='read from database',
        )
        parser.add_argument(
            '--write_csv',
            action='store_true',
            help='write csv data to database',
        )
        parser.add_argument(
            '--write_json',
            action='store_true',
            help='write json data to database',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='write json data to database',
        )

    def write_db(self, data, ext):
        """Function for write to db table."""
        if ext not in ('JSON', 'CSV'):
            return CommandError('Unknown extension')
        if ext == 'JSON':
            self.stdout.write('JSON файл обнаружен. Начинаю запись в БД.')
            for obj in data:
                Ingredient.objects.get_or_create(**obj)
            self.stdout.write('Данные из JSON успешно импортированы в БД.')
        elif ext == 'CSV':
            self.stdout.write('CSV файл обнаружен. Начинаю запись в БД.')
            for obj in data:
                Ingredient.objects.get_or_create(
                    name=obj[0],
                    measurement_unit=obj[1]
                )
            self.stdout.write('Данные из CSV успешно импортированы в БД.')
        self.stdout.write('Конец работы функции записи в БД.')
        return None

    def read_db(self):
        """Function for read from db table."""
        for obj in Ingredient.objects.all():
            print(obj, end='\n')
        self.stdout.write('Данные успешно прочитаны.')

    def delete_db(self):
        """Function for delete from db table."""
        Ingredient.objects.all().delete()
        self.stdout.write('Данные успешно удалены.')

    def handle(self, **options):
        if not (
            options.get("read")
            or options.get("write_csv")
            or options.get("write_json")
            or options.get("delete")
        ):
            raise CommandError(
                'Use --read, --delete, --write_csv or --write_json argument'
            )
        filename = 'ingredients'
        data_folder = 'data/'
        json_file = os.path.join(data_folder, f'{filename}.json')
        csv_file = os.path.join(data_folder, f'{filename}.csv')
        if options['write_csv']:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_data = csv.reader(file, delimiter=',')
                self.write_db(csv_data, 'CSV')
        if options['write_json']:
            with open(json_file, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                self.write_db(json_data, 'JSON')
        if options['read']:
            self.read_db()
        if options['delete']:
            self.delete_db()
