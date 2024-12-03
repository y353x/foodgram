from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from djoser.conf import settings
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.constants import ACTION_ME
from user.models import Follow, User
from user.serializers import AvatarSerializer, FollowSerializer, UserSerializer


class UserViewSet(djoser_views.UserViewSet):
    """Вьюсет для пользователя из модуля Djoser."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Запрет входа на эндпоинт me анониму."""
        if self.action == ACTION_ME:
            self.permission_classes = settings.PERMISSIONS.user_me
        return super().get_permissions()

    @action(
        methods=['POST', 'PUT', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Добавление/удаление аватара."""
        instance = self.get_instance()
        data = self.request.data
        if data and (request.method in ('POST', 'PUT')):
            serializer = AvatarSerializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif request.method == 'DELETE':
            data = {'avatar': None}
            serializer = AvatarSerializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise ValidationError('Введены некорректные данные.')

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        follow_list = Follow.objects.filter(user=self.request.user)
        follow_pages = self.paginate_queryset(follow_list)
        serializer = FollowSerializer(
            follow_pages,
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """Подписка на/отписка от автора."""
        author = get_object_or_404(User, id=id)
        user = request.user

        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'author': id,
                      'user': user.id},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        subscription = Follow.objects.filter(user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
