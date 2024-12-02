from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeListSerializer,
                             RecipeSerializer, TagSerializer)
from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from recipes.shopping_list import shopping_list
from shortlink.models import ShortLink
from shortlink.serializers import ShortLinkSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
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
        elif self.action == 'favorite':
            return FavoriteSerializer
        elif self.action == 'shopping_cart':
            return CartSerializer
        return RecipeSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта в избранное."""
        if request.method == 'POST':
            return self._cart_favorite_post(request, pk)
        return self._cart_favorite_delete(request, pk, Favorite)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта в корзину."""
        if request.method == 'POST':
            return self._cart_favorite_post(request, pk)
        return self._cart_favorite_delete(request, pk, Cart)

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
        return shopping_list(queryset)

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

    def _cart_favorite_post(self, request, pk):
        """Добавление объекта в избранное/корзину."""
        user = request.user
        serializer = self.get_serializer(
            data={'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def _cart_favorite_delete(self, request, pk, model):
        """Удаление объекта из избранного/корзины."""
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        model_recipe = model.objects.filter(recipe=recipe, user=user)
        if model_recipe.exists():
            model_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
