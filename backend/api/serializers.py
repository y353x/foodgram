from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from api.constants import INGREDIENT_AMOUNT
from recipes.models import (Cart, Favorite, Ingredient, IngredientRecipe,
                            Recipe, Tag)
from user.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тэгов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


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


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для записи ингредиентов с полем amount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < INGREDIENT_AMOUNT:
            raise ValidationError(
                detail=f'ингредиента < {INGREDIENT_AMOUNT}',
                code=status.HTTP_400_BAD_REQUEST)
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    ingredients = IngredientWriteSerializer(
        many=True,
        write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True)
    image = Base64ImageField(required=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time', 'author',)
        extra_kwargs = {'ingredients': {'required': True},
                        'cooking_time': {'required': True},
                        'image': {'required': True},
                        'tags': {'required': True},
                        'name': {'required': True},
                        'text': {'required': True}}

    def validate(self, attrs):
        """Валидация тэгов, ингредиентов."""
        tags = attrs.get('tags')
        image = attrs.get('image')
        ingredients = attrs.get('ingredients')

        if not image:
            raise ValidationError(
                detail='добавьте фото рецепта.',
                code=status.HTTP_400_BAD_REQUEST)
        if not tags:
            raise ValidationError(
                detail='добавьте теги.',
                code=status.HTTP_400_BAD_REQUEST)
        if len(tags) > len(set(tags)):
            raise ValidationError(
                detail='тэги повторяются.',
                code=status.HTTP_400_BAD_REQUEST)
        if not ingredients:
            raise ValidationError(
                detail='добавьте ингредиенты.',
                code=status.HTTP_400_BAD_REQUEST)
        uniq_ingredients = set(ingredient['id'] for ingredient in ingredients)
        if len(ingredients) > len(uniq_ingredients):
            raise ValidationError(
                detail='повторяющиеся ингредиенты.',
                code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self._add_ingredients(IngredientRecipe, recipe, ingredients, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        self._add_ingredients(IngredientRecipe, instance, ingredients, tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def _add_ingredients(self, model, recipe, ingredients, tags):
        model.objects.bulk_create(
            model(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']) for ingredient in ingredients
        )
        recipe.tags.set(tags)
        return recipe


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
        return user.is_authenticated and user.favorites.filter(
            recipe_id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and user.carts.filter(
            recipe_id=obj.id).exists()


class RecipeFollowSerializer(serializers.ModelSerializer):
    """Сериалайзер для вывода списка рецептов
    в запросах подписки, избранном и корзине.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image',)


class CartFavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для наследования Избранного и Корзины."""

    class Meta:
        model = None
        fields = ('user', 'recipe')
        read_only_fields = ('user',)

    def validate(self, attrs):
        recipe = attrs['recipe']
        user = self.context['request'].user
        if self.Meta.model.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('рецепт уже добавлен.')
        return super().validate(attrs)

    def to_representation(self, instance):
        return RecipeFollowSerializer(
            instance.recipe,
            context=self.context
        ).data


class FavoriteSerializer(CartFavoriteSerializer):
    """Сериалайзер для избранного."""

    class Meta(CartFavoriteSerializer.Meta):
        model = Favorite


class CartSerializer(CartFavoriteSerializer):
    """Сериалайзер для корзины."""

    class Meta(CartFavoriteSerializer.Meta):
        model = Cart
