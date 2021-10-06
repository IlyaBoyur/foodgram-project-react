from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("users", views.UserViewSet, basename='users')
router.register("ingredients", views.IngredientViewSet, basename='ingredients')
router.register("tags", views.TagViewSet, basename='tags')
router.register("recipes", views.RecipeViewSet, basename='recipes')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
