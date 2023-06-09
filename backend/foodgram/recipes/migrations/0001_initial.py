# Generated by Django 4.2.1 on 2023-05-31 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=60, unique=True, verbose_name="Название тэга"
                    ),
                ),
                (
                    "colour",
                    models.CharField(max_length=7, unique=True, verbose_name="Цвет"),
                ),
                (
                    "slug",
                    models.SlugField(max_length=200, unique=True, verbose_name="Слаг"),
                ),
            ],
            options={
                "verbose_name": "Тэг",
                "verbose_name_plural": "Тэги",
            },
        ),
    ]
