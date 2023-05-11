from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Tag(models.Model):
    """Модель тегов"""
    BLUE = '#4682B4'
    ORANGE = '#FF4500'
    GREEN = '#006400'
    PURPLE = '#9370DB'
    YELLOW = '#FFD700'

    COLOR_CHOICES = [
        (BLUE, 'Синий'),
        (ORANGE, 'Оранжевый'),
        (GREEN, 'Зеленый'),
        (PURPLE, 'Фиолетовый'),
        (YELLOW, 'Желтый'),
    ]
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200,
        help_text='Название тега',
        unique=True
    )
    color = models.CharField(
        verbose_name='Цвет тега',
        max_length=7,
        null=True,
        choices=COLOR_CHOICES,
        validators=[
            RegexValidator(
                '^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Укажите HEX-код выбранного цвета')
        ]
    )
    slug = models.SlugField(
        verbose_name='slug тега',
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                '^[-a-zA-Z0-9_]+$',
                message='Можно использовать только буквы '
                        'английского алфавита, цифры и знак подчёркивания')
        ]
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
        help_text='Название ингредиента',
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=200,
        help_text='Единица измерения',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredients'
            )
        ]

    def __str__(self) -> str:
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        help_text='Название рецепта',
    )
    image = models.ImageField(
        upload_to='media/',
        null=True,
        default=None,
    )
    text = models.TextField()
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
    )
    amount_ingredients = models.ManyToManyField(Ingredient,
                                                through='RecipeIngredient')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связанная таблица для рецептов и ингредиентов"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Рецепт',

    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=(
            MinValueValidator(
                1,
                message='Количество ингредиентов не может быть меньше 1'
            ),
        ),
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe'
            )
        ]

    def __str__(self):
        return (f'{self.recipe.name}: '
                f'{self.ingredient.name} - '
                f'{self.amount} '
                f'{self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """Модель избранного"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite'

    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.recipe.name}'


class Cart(models.Model):
    """Модель для списка покупок"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Корзина',
        related_name='cart',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='cart',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина',
        verbose_name_plural = 'Корзина'
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.recipe.name}'
