# Generated by Django 4.2.1 on 2023-06-03 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0005_shoppingcart_shoppingcart_unique_shopping_cart"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="description",
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
