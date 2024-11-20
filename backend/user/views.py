from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from djoser.conf import settings
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import Follow, User
from user.serializers import AvatarSerializer, FollowSerializer, UserSerializer


class UserViewSet(djoser_views.UserViewSet):
    """Viewset для пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Запрет входа на эндпоинт me анониму."""
        if self.action == "me":
            self.permission_classes = settings.PERMISSIONS.user_me
        return super().get_permissions()

    @action(
        methods=['put', 'post', 'delete'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
        url_name='me-avatar',
    )
    def avatar(self, request):
        """Добавление/удаление аватара"""
        instance = self.get_instance()
        if self.request.data and (request.method == 'POST' or 'PUT'):
            serializer = AvatarSerializer(instance,
                                          data=self.request.data,
                                          partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
        elif request.method == 'DELETE':
            data = {'avatar': None}
            serializer = AvatarSerializer(instance, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('Введены некорректные данные.')

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
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
        methods=['DELETE', 'POST'],
        detail=True,
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if Follow.objects.filter(
                    author=author, user=user).exists():
                raise ValidationError(
                    detail='Вы уже подписаны на этого пользователя!',
                    code=status.HTTP_400_BAD_REQUEST)
            if user == author:
                raise ValidationError(
                    detail='Невозможно подписаться на себя!',
                    code=status.HTTP_400_BAD_REQUEST)
            serializer = FollowSerializer(
                data={'author': author},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user, author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            author = get_object_or_404(User, id=id)
            user = request.user
            subscription = Follow.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND)


# class FollowViewSet(mixins.CreateModelMixin,
#                     mixins.ListModelMixin,
#                     viewsets.GenericViewSet):
#     """Вьюсет подписок."""
#     queryset = Follow.objects.all()
#     serializer_class = FollowSerializer
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ('author__username',)

#     def get_queryset(self):
#         current_user = self.request.user
#         return current_user.follower.all()

#     def perform_create(self, serializer):
#         author_id = self.kwargs.get('pk')
#         author = get_object_or_404(User, id=author_id)
#         user = self.request.user
#         if Follow.objects.filter(
#                 author=author,
#                 user=user).exists():
#             raise ValidationError(
#                 detail='Вы уже подписаны на этого пользователя!',
#                 code=status.HTTP_400_BAD_REQUEST)
#         if user == author:
#             raise ValidationError(
#                 detail='Невозможно подписаться на себя!',
#                 code=status.HTTP_400_BAD_REQUEST)
#         serializer.save(user=user,
#                         author=author)

# class UserViewSet(viewsets.ModelViewSet):
#     """Viewset для пользователя"""
#     queryset = User.objects.all()
#     # permission_classes = (IsCurrentUserOrAdminOrReadOnly, )
#     permission_classes = (AllowAny, )
#     # pagination_class = ApiPagination
#     serializer_class = UserSerializer
#     @action(
#         methods=["get"],
#         detail=False,
#         url_path="me",
#         permission_classes=(permissions.IsAuthenticated,),
#         serializer_class=UserSerializer,
#     )
#     def users_own_profile(self, request):
#         user = request.user
#         serializer = self.get_serializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
