from django.contrib.auth import get_user_model
from django.db.models import When, Case
from django.shortcuts import get_object_or_404
from api.paginators import PageLimitPagination
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from djoser import utils as djoser_utils
from djoser import views as djoser_views
from djoser.conf import settings as djoser_settings


User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    http_method_names = ['get', 'post']
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return super().get_queryset().annotate(is_subscribed=Case(
            When(id__in=self.request.user.subscribed_to.values('author_id'),
                 then=True),
            default=False
        ))

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        return Response(
            self.get_serializer(
                get_object_or_404(self.get_queryset(),
                                  id=request.user.id)
            ).data
        )


class TokenCreateView(djoser_views.TokenCreateView):
    def _action(self, serializer):
        token = djoser_utils.login_user(self.request, serializer.user)
        token_serializer_class = djoser_settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED,
        )


class TokenDestroyView(djoser_views.TokenDestroyView):
    def post(self, request):
        djoser_utils.logout_user(request)
        return Response(status=status.HTTP_201_CREATED)
