from datetime import date

from api.filters import RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeListSerializer,
                             RecipeSerializer, TagSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from shortlink.models import ShortLink
from shortlink.serializers import ShortLinkSerializer


class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для ингридиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('name',)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для рецептов."""

    queryset = Recipe.objects.select_related(
        'author').prefetch_related('ingredients', 'tags')
    permission_classes = (IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта в избранное."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'recipe': recipe},
                context={'request': request,
                         'recipe': recipe})
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite_recipe = Favorite.objects.filter(recipe=recipe, user=user)
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user

        if request.method == 'POST':
            serializer = CartSerializer(
                data={'recipe': recipe},
                context={'request': request,
                         'recipe': recipe})
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            favorite_recipe = Cart.objects.filter(recipe=recipe, user=user)
            if favorite_recipe.exists():
                favorite_recipe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Выгрузка ингридиентов из рецептов корзины."""
        user = request.user
        queryset = Cart.objects.filter(user=user).values_list(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit').annotate(
            amount=Sum('recipe__ingredient_recipe__amount'))
        shop_list = f'Список покупок на {date.today()}:'
        for position in queryset:
            row = f'\n{position[0]} - {position[2]} {position[1]}.'
            shop_list += row
        filename = f'shop_list_{date.today()}.txt'
        response = HttpResponse(
            shop_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(
        methods=['GET'],
        detail=True,
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk):
        """Создание/выдача короткой ссылки на рецепт."""
        get_object_or_404(Recipe, id=pk)  # Ссылка только при наличии рецепта.
        full_url = request.path[4:-9]
        if ShortLink.objects.filter(full=full_url).exists():
            link_object = ShortLink.objects.get(full=full_url)
            serializer = ShortLinkSerializer(link_object)
        else:
            serializer = ShortLinkSerializer(
                data={'full': full_url},
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
        s_link = serializer.data.get('short')
        response_data = {'short-link': s_link}
        return Response(response_data, status=status.HTTP_200_OK)
