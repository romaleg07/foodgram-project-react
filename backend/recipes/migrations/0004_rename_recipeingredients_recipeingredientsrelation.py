# Generated by Django 4.1.7 on 2023-03-07 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredients_name_alter_recipes_name_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RecipeIngredients',
            new_name='RecipeIngredientsRelation',
        ),
    ]
