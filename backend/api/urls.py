from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from user.views import FollowViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register(r"users/(?P<pk>\d+)/subscribe", FollowViewSet, basename='subscribe')

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]
