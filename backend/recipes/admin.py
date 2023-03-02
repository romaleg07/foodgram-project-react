from django.contrib import admin

from .models import Ingredients, Recipes, Tags


class TagsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipesAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'image',
        'name',
        'text',
        'cooking_time',
        'author',
        'pub_date'
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Tags, TagsAdmin)
admin.site.register(Ingredients, IngredientsAdmin)
admin.site.register(Recipes, RecipesAdmin)
