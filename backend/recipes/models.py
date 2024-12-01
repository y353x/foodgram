from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import Truncator

from api.constants import (COOKING_TIME, INGREDIENT_MEASURE,
                           MAX_ADMIN_NAME_LENGTH, NAME_LENGTH,
                           SHORT_NAME_LENGTH, TAG_LENGTH, UNIT_NAME_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель ингридиентов.

    Атрибуты
    --------
    name : str
        уникальное название
    measurement_unit : str
        единица измерения
    """

    name = models.CharField(verbose_name='Название',
                            unique=True,
                            max_length=SHORT_NAME_LENGTH,
                            help_text='уникальное название',
                            db_index=True,)
    measurement_unit = models.CharField(verbose_name='Единица измерения',
                                        max_length=UNIT_NAME_LENGTH,
                                        help_text='единица измерения')

    class Meta:
        ordering = ('name',)
        # default_related_name = 'ingredient'
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='name_measurement_unit',
            )
        ]

    def __str__(self):
        return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


class Tag(models.Model):
    """
    Модель тэгов.

    Атрибуты
    --------
    name : str
        уникальное название
    slug : str
        уникальный тэг
    """

    name = models.CharField(verbose_name='Название',
                            unique=True,
                            max_length=TAG_LENGTH,
                            help_text='уникальное название')
    slug = models.SlugField(verbose_name='Тэг',
                            unique=True,
                            max_length=TAG_LENGTH,
                            help_text='уникальный тэг')

    class Meta:
        ordering = ('name',)
        # default_related_name = 'tag'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE)
    name = models.CharField(
        verbose_name='Название',
        max_length=NAME_LENGTH)
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/',
        help_text='Загрузите фото блюда/рецепта')
    text = models.TextField(
        verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientRecipe')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время пригтовления в минутах',
        default=COOKING_TIME,
        validators=[
            MinValueValidator(
                COOKING_TIME,
                f'Время приготовления не менее {COOKING_TIME} минут(ы).')])
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'name'],
                name='unique_author_name'),
        )

    def __str__(self):
        return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


class IngredientRecipe(models.Model):
    """Промежуточная таблица с весом ингредиента в рецепте."""

    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='ingredient_recipe',)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        help_text='Введите количество ингредиента в его ед.измерения',
        default=INGREDIENT_MEASURE,
        validators=[MinValueValidator(
            INGREDIENT_MEASURE,
            f'Количество ингредиента не менее {INGREDIENT_MEASURE} ед.изм.')])

    class Meta:
        ordering = ('id',)
        verbose_name = 'Cостав'
        verbose_name_plural = 'Состав'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredients')]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class CartFavorite(models.Model):
    """Абстрактная модель для корзины и избранного."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name='Рецепт')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_recipe_user')]


class Cart(CartFavorite):
    """Корзина покупок."""

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзина'
        default_related_name = 'carts'

    def __str__(self):
        return f'{self.recipe.name} в корзине.'


class Favorite(CartFavorite):
    """Избранное."""

    class Meta:
        ordering = ('recipe__name',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.recipe.name} в избранном.'

# from django.contrib.auth import get_user_model
# from django.core.validators import MinValueValidator
# from django.db import models
# from django.utils.text import Truncator

# from api.constants import (MAX_ADMIN_NAME_LENGTH, NAME_LENGTH,
#                            SHORT_NAME_LENGTH, TAG_LENGTH, UNIT_NAME_LENGTH)

# User = get_user_model()


# class Ingredient(models.Model):
#     """Модель ингридиентов.
#     Название (name) и ед.измерения (slug).
#     """

#     name = models.CharField(verbose_name='Название',
#                             unique=True,
#                             max_length=SHORT_NAME_LENGTH,
#                             help_text='уникальное название',
#                             db_index=True,)
#     measurement_unit = models.CharField(verbose_name='Единица измерения',
#                                         max_length=UNIT_NAME_LENGTH,
#                                         help_text='единица измерения')

#     class Meta:
#         ordering = ('id',)
#         default_related_name = 'ingredient'
#         verbose_name = 'Ингридиент'
#         verbose_name_plural = 'Ингридиенты'

#     def __str__(self):
#         return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


# class Tag(models.Model):
#     """Модель тэгов.
#     Название (name) и слаг (slug).
#     """

#     name = models.CharField(verbose_name='Название',
#                             unique=True,
#                             max_length=TAG_LENGTH,
#                             help_text='уникальное название')
#     slug = models.SlugField(verbose_name='Тэг',
#                             unique=True,
#                             max_length=TAG_LENGTH,
#                             help_text='уникальный тэг')

#     class Meta:
#         ordering = ('id',)
#         default_related_name = 'tag'
#         verbose_name = 'Тэг'
#         verbose_name_plural = 'Тэги'

#     def __str__(self):
#         return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


# class Recipe(models.Model):
#     """Модель рецепта."""

#     author = models.ForeignKey(
#         User,
#         verbose_name='Автор рецепта',
#         on_delete=models.CASCADE)
#     name = models.CharField(
#         verbose_name='Название',
#         max_length=NAME_LENGTH)
#     image = models.ImageField(
#         verbose_name='Фото блюда',
#         upload_to='recipes/',
#         help_text='Загрузите фото блюда/рецепта')
#     text = models.TextField(
#         verbose_name='Описание')
#     ingredients = models.ManyToManyField(
#         Ingredient,
#         verbose_name='Ингредиенты',
#         through='IngredientRecipe')
#     tags = models.ManyToManyField(
#         Tag,
#         verbose_name='Тэги')
#     cooking_time = models.PositiveSmallIntegerField(
#         verbose_name='Время приготовления',
#         help_text='Введите время пригтовления в минутах',
#         default=1,
#         validators=[
#             MinValueValidator(
#                 1, 'Время приготовления не менее 1 минуты.')])
#     pub_date = models.DateTimeField(
#         verbose_name='Дата и время публикации',
#         auto_now_add=True)

#     class Meta:
#         ordering = ('-pub_date',)
#         default_related_name = 'recipes'
#         verbose_name = 'Рецепт'
#         verbose_name_plural = 'Рецепты'
#         constraints = (
#             models.UniqueConstraint(
#                 fields=['author', 'name'],
#                 name='unique_author_name'),
#         )

#     def __str__(self):
#         return Truncator(self.name).chars(MAX_ADMIN_NAME_LENGTH)


# class IngredientRecipe(models.Model):
#     """Промежуточная таблица с весом ингридиента в рецепте."""

#     recipe = models.ForeignKey(Recipe,
#                                on_delete=models.CASCADE,
#                                related_name='ingredient_recipe',)
#     ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
#     amount = models.PositiveSmallIntegerField(
#         verbose_name='Количество ингридиента',
#         help_text='Введите количество ингридиента в его ед.измерения',
#         default=1,
#         validators=[MinValueValidator(
#             1, 'Количество ингридиента не менее 1 ед.измерения.')])

#     class Meta:
#         ordering = ('id',)
#         verbose_name = 'Cостав'
#         verbose_name_plural = 'Состав'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['recipe', 'ingredient'],
#                 name='unique_recipe_ingredients')]

#     def __str__(self):
#         return f'{self.ingredient} {self.amount}'


# class CartFavorite(models.Model):
#     """Абстрактная модель для корзины и избранного."""

#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
#                                verbose_name='Рецепт')
#     user = models.ForeignKey(User, on_delete=models.CASCADE,
#                              verbose_name='Пользователь')

#     class Meta:
#         abstract = True
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['recipe', 'user'],
#                 name='unique_recipe_user')]


# class Cart(CartFavorite):
#     """Корзина покупок."""

#     class Meta:
#         verbose_name = 'Корзина'
#         verbose_name_plural = 'Корзина'
#         default_related_name = 'cart'


# class Favorite(CartFavorite):
#     """Избранное."""

#     class Meta:
#         verbose_name = 'Избранное'
#         verbose_name_plural = 'Избранное'
#         default_related_name = 'favorite'
