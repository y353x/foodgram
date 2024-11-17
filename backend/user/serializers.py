import base64  # Модуль с функциями кодирования и декодирования base64
import re

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

import api.serializers as api_serializers
from recipes.models import Recipe
from user.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Преобразование изображения из Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='avatar.' + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=150)
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
        if self.context.get('request') is not None:
            user = self.context.get('request').user
            if not user.is_anonymous:
                return bool(Follow.objects.filter(
                    user_id=user.id,
                    author_id=obj.id).exists())
            else:
                return False
        else:
            return False


class UserCreateSerializer(serializers.ModelSerializer):

    username = serializers.CharField(max_length=150)

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
        if not re.fullmatch(r'^[\w.@+-]+\Z', value):
            raise ValidationError(
                'username должен соответствовать "^[\w.@+-]+\Z"')
        elif User.objects.filter(username=value).exists():
            raise ValidationError(
                'username занят')
        return value

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

    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    avatar = serializers.ImageField(source='author.avatar',
                                    read_only=True)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user_id=user.id,
                author_id=obj.author_id).exists()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.author)
        return api_serializers.RecipeFollowSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        recipes_count = Recipe.objects.filter(author=obj.author).count()
        return recipes_count

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'avatar',
                  'recipes', 'recipes_count',
                  'first_name', 'last_name', 'is_subscribed')
