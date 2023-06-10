from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet

v1_router = DefaultRouter()
v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(v1_router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
