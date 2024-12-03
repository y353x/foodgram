import re

from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

import api.serializers as api_serializers
from api.constants import ACTION_ME, REGEX_VALIDATION, USERNAME_LENGTH
from user.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер модели пользователя."""

    username = serializers.CharField(max_length=USERNAME_LENGTH)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'avatar'
                  )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request is not None and request.user.is_authenticated and obj.
                authors.filter(user=request.user).exists())


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер модели пользователя для создания."""

    username = serializers.CharField(max_length=USERNAME_LENGTH)

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'password'
                  )
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if value == ACTION_ME:
            raise ValidationError(
                'Недопустимое имя')
        if not re.fullmatch(REGEX_VALIDATION, value):
            raise ValidationError(
                f'username должен соответствовать {REGEX_VALIDATION}')
        if User.objects.filter(username=value).exists():
            raise ValidationError(
                f'username {value} занят')
        return value

    # Для формирования паролей с кодированием.
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    class Meta:
        model = Follow
        fields = ('author', 'user')

    def validate(self, attrs):
        user_id = attrs['user']
        author_id = attrs['author']
        if Follow.objects.filter(
                author=author_id, user=user_id).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user_id == author_id:
            raise ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return super().validate(attrs)

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.author,
            context=self.context
        ).data


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор вывода подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Получение рецептов автора (с возможностью ограничения кол-ва)."""
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit_str = request.query_params.get('recipes_limit', 'nope')
        if recipes_limit_str.isdigit():
            recipes_limit = int(recipes_limit_str)
            recipes = recipes[:recipes_limit]
        return api_serializers.RecipeFollowSerializer(recipes,
                                                      context=self.context,
                                                      many=True).data
