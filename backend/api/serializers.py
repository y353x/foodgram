import base64  # Модуль с функциями кодирования и декодирования base64

from django.core.files.base import ContentFile
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')
        read_only_fields = ('__all__',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('__all__',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиентов с количеством."""

    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('__all__',)


class Base64ImageField(serializers.ImageField):
    """Преобразование изображения из Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='recipe.' + ext)
        return super().to_internal_value(data)


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для записи ингредиентов с полем amount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    ingredients = IngredientWriteSerializer(
        many=True,
        write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField()
    author = UserSerializer(
        read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Cart.objects.filter(recipe=obj).exists()
        return False

    def validate(self, attrs):
        """Валидация тэгов, ингредиентов."""
        tags = attrs.get('tags')
        ingredients = attrs.get('ingredients')

        if not tags:
            raise ValidationError(
                detail='добавьте теги.',
                code=status.HTTP_400_BAD_REQUEST)
        elif len(tags) > len(set(tags)):
            raise ValidationError(
                detail='тэги повторяются.',
                code=status.HTTP_400_BAD_REQUEST)
        elif not ingredients:
            raise ValidationError(
                detail='добавьте ингредиенты.',
                code=status.HTTP_400_BAD_REQUEST)
        uniq_ingredients = set(ingredient['id'] for ingredient in ingredients)
        if len(ingredients) > len(uniq_ingredients):
            raise ValidationError(
                detail='повторяющиеся ингредиенты.',
                code=status.HTTP_400_BAD_REQUEST)
        for ingredient in ingredients:
            if ingredient['amount'] < 1:
                raise ValidationError(
                    detail='ингредиента < 1',
                    code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        for ingredient in ingredients:
            IngredientRecipe.objects.update_or_create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount'])
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        value = super().to_representation(instance)
        value['ingredients'] = IngredientRecipeSerializer(
            instance.ingredient_recipe.all(), many=True).data
        value['tags'] = TagSerializer(
            instance.tags.all(), many=True).data
        return value

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author',
                  'is_favorited', 'is_in_shopping_cart',)
        extra_kwargs = {'ingredients': {'required': True},
                        'cooking_time': {'required': True},
                        'tags': {'required': True},
                        'name': {'required': True},
                        'text': {'required': True}}


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка рецептов."""

    author = UserSerializer()
    tags = TagSerializer(
        many=True,
        read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='ingredient_recipe',
        read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Favorite.objects.filter(
                user_id=user.id,
                recipe_id=obj.id).exists()
        else:
            return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Cart.objects.filter(
                user_id=user.id,
                recipe_id=obj.id).exists()
        else:
            return False


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка рецептов
    в запросах подписки.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)
        read_only_fields = ('__all__',)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер.
    """

    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(
                detail='рецепт уже в избранном.',
                code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'cooking_time', 'image',)
        read_only_fields = ('__all__',)


class CartSerializer(serializers.ModelSerializer):
    """Сериалайзер.
    """

    name = serializers.ReadOnlyField(
        source='recipe.name',
        read_only=True)
    image = serializers.ImageField(
        source='recipe.image',
        read_only=True)
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
        read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        read_only=True)

    def validate(self, attrs):
        user = self.context.get('request').user
        recipe = self.context.get('recipe')
        if Cart.objects.filter(recipe=recipe, user=user).exists():
            raise ValidationError(
                detail='рецепт уже в корзине.',
                code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    class Meta:
        model = Cart
        fields = ('id', 'name', 'cooking_time', 'image',)
        read_only_fields = ('__all__',)
