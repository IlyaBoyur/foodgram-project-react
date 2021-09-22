from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api import views


router = DefaultRouter()
router.register("users", views.UserViewSet, basename='users')


urlpatterns = [
    path('auth/token/login/',
         views.TokenCreateView.as_view(),
         name="token_login"),
    path('auth/token/logout/',
         views.TokenDestroyView.as_view(),
         name="token_logout"),
    path('', include(router.urls)),
]
