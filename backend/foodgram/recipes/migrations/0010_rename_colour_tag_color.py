# Generated by Django 3.2.19 on 2023-06-15 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_recipeingredient_unique_ingredient_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tag',
            old_name='colour',
            new_name='color',
        ),
    ]
