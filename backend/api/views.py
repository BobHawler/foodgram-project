from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import Cart, Favorite, Ingredient, Recipe, Tag
from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import CreateListViewSet
from .pagination import LimitPageNumberPaginator
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (CartSerializer, FavoriteSerializer,
                          IngredientSerializer, RecipeIngredient,
                          RecipeSerializer, RecipeWriteSerializer,
                          SubscribeSerializer, TagSerializer)

User = get_user_model


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Tag"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    http_method_names = ('get',)
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Ingredient"""
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Recipe"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPaginator

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def favorite_and_shopping_cart_add(model, user, recipe, serializer):
        model_create, create = model.objects.get_or_create(user=user,
                                                           recipe=recipe)
        if create:
            return Response(
                serializer.to_representation(instance=model_create),
                status=status.HTTP_201_CREATED
                )
        return None

    @staticmethod
    def favorite_and_shopping_cart_delete(model, user, recipe):
        model.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        filter_backends=DjangoFilterBackend,
        filterset_class=RecipeFilter,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.favorite_and_shopping_cart_add(
                Favorite, user, recipe, FavoriteSerializer(),)
        if request.method == 'DELETE':
            return self.favorite_and_shopping_cart_delete(
                Favorite, user, recipe)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            return self.favorite_and_shopping_cart_add(
                Cart, user, recipe, CartSerializer(),)
        if request.method == 'DELETE':
            return self.favorite_and_shopping_cart_delete(
                Cart, user, recipe)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,)
            )
    def download_shopping_cart(self, request):
        file_name = 'shopping_list.txt'
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_sum=Sum('amount')).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'ingredient_sum')
        content = ''
        for ingredient in ingredients:
            content += (
                f'{ingredient[0]} '
                f'{ingredient[2]} '
                f'- {ingredient[1]}\r\n'
            )
        response = HttpResponse(
            content, content_type='text/plain', charset='utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response


class SubscribeViewSet(CreateListViewSet):
    """Вьюсет модели Subscription."""
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('user__username', 'author__username')

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
