# Generated by Django 4.2.1 on 2023-06-14 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0008_alter_shoppingcart_recipe_alter_shoppingcart_user"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="recipeingredient",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"), name="unique_ingredient"
            ),
        ),
        migrations.AddConstraint(
            model_name="recipetag",
            constraint=models.UniqueConstraint(
                fields=("recipe", "tag"), name="unique_tag"
            ),
        ),
    ]
