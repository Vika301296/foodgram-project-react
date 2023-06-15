import csv
import os
from sys import stdout

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        load_ingredients()


def load_ingredients():
    print("Начинаем импорт ингредиентов.")
    with open('data/ingredients.csv', newline='') as csvfile:
        try:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(csvreader)
            for row in csvreader:
                obj = Ingredient(
                    name=row[0],
                    measurement_unit=row[1]
                )
                obj.save()
            print("Импорт ингедиентов успешно завершен!")
        except CommandError:
            stdout('Файл не найден!')
