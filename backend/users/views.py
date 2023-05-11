from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import LimitPageNumberPaginator
from api.serializers import (SubscribeSerializer, SubscribeWriteSerializer,
                             UserSerializer)
from .models import Subscription, User


class UserViewSet(UserViewSet):
    """Вьюсет для модели User"""
    pagination_class = LimitPageNumberPaginator
    serializer_class = UserSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=LimitPageNumberPaginator)
    def subscriptions(self, request):
        queryset = User.objects.filter(subscription__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(page, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['id'])

        if request.method == 'POST':
            serializer = SubscribeWriteSerializer(
                author, data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.get_or_create(user=request.user,
                                               author=author)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
        return Response({'detail': 'Вы успешно отписались от автора.'},
                        status=status.HTTP_204_NO_CONTENT)
