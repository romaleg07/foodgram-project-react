# Generated by Django 4.1.7 on 2023-03-07 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipeingredients_delete_recipeingredientsrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipes',
            name='ingredients',
            field=models.ManyToManyField(related_name='ingredients', through='recipes.RecipeIngredients', to='recipes.ingredients', verbose_name='Ингредиенты'),
        ),
    ]
