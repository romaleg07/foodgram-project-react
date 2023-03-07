from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tags(models.Model):
    name = models.CharField('Заголовок', max_length=200, db_index=True)
    color = models.CharField('Цвет', max_length=7)
    slug = models.SlugField('ссылка', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField('Название', max_length=200, db_index=True)
    measurement_unit = models.CharField('Еденица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipes(models.Model):
    ingredients = models.ManyToManyField(
        Ingredients,
        related_name='ingredients',
        verbose_name='Ингредиенты',
        through="RecipeIngredients"
    )
    tags = models.ManyToManyField(
        Tags,
        related_name='tags',
        verbose_name='Теги'
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/',
    )
    name = models.CharField('Название', max_length=200, db_index=True)
    text = models.TextField(
        verbose_name='Рецепт',
        help_text='Рецепт'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(1)
        ]
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:30]


class RecipeIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        related_name='amount',
        validators=[MinValueValidator(1, message='Минимальное количество 1!')]
    )

    def __str__(self):
        return f'{self.ingredient} в {self.recipe}'

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='userfavorite',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favorite'
            ),
        )

    def __str__(self):
        return self.recipe + ' изрбранный для ' + self.user


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipes,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_cart'
    )

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique recipe in shopping cart'
            ),
        )

    def __str__(self):
        return self.recipe + ' в корзине у ' + self.user
