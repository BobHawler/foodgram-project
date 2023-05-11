from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.serializers import PrimaryKeyRelatedField
from rest_framework.settings import api_settings

from api.fields import Base64ImageField
from users.models import Subscription, User
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscription.objects.filter(user=self.context['request'].
                                               user,
                                               author=obj).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""
    is_subscribed = serializers.SerializerMethodField()
    password = serializers.CharField(style={"input_type": "password"},
                                     write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )

    def create(self, validated_data):
        try:
            user = self.perform_create(validated_data)
        except IntegrityError:
            self.fail("cannot_create_user")

        return user

    def validate(self, attrs):
        user = User(**attrs)
        password = attrs.get('password')

        try:
            validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[
                    api_settings.NON_FIELD_ERRORS_KEY
                    ]}
            )

        return attrs

    def get_is_subscribed(self, obj):
        if (self.context.get('request')
           and not self.context['request'].user.is_anonymous):
            return Subscription.objects.filter(user=self.context['request'].
                                               user,
                                               author=obj).exists()
        return False

    def perform_create(self, validated_data):
        with transaction.atomic():
            return User.objects.create_user(**validated_data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Recipe_ingredient"""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = RecipeIngredient


class IngredientIdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    amount = serializers.IntegerField(required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количесто ингредиента не может быть пустым.'
            )
        return value


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Recipe (GET)"""
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Cart.objects.filter(recipe=obj, user=request.user).exists()
        return False


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сокращённый сериалайзер для модели Recipe"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Recipe (POST, UPDATE, DELETE)"""
    ingredients = IngredientIdSerializer(many=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField(required=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        if len(ingredients) != len(set([item['id'] for item in ingredients])):
            raise serializers.ValidationError(
                'Вы добавили несколько одинаковых ингредиентов. Ингредиенты '
                'должны быть уникальными.')
        return data

    def add_ingredient(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)
        self.add_ingredient(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.add(*tags)
        self.add_ingredient(instance, ingredients)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Favorite"""
    id = serializers.CharField(read_only=True, source='recipe.id')
    cooking_time = serializers.CharField(read_only=True,
                                         source='recipe.cooking_time')
    name = serializers.CharField(read_only=True, source='recipe.name')
    image = serializers.CharField(read_only=True, source='recipe.image')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError('Вы уже добавили этот рецепт '
                                              'в избранное!')
        return data


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Subscription (GET)"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            return ShortRecipeSerializer(
                Recipe.objects.filter(author=obj)[:int(recipes_limit)],
                many=True,
                context={'request': request}
            ).data
        return ShortRecipeSerializer(
                Recipe.objects.filter(author=obj),
                many=True,
                context={'request': request}
            ).data

    def get_is_subscribed(self, obj):
        return (self.context.get('request').user.is_authenticated
                and Subscription.objects.filter(user=self.context['request'].
                                                user,
                                                author=obj).exists())


class SubscribeWriteSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели Subscription (POST)"""
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, obj):
        if self.context['request'].user == obj:
            raise serializers.ValidationError({'errors': 'Какая-то ошибка.'
                                               'Смиритесь, пожалуйста.'})
        return obj

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists())

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CartSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Cart"""
    id = serializers.CharField(read_only=True, source='recipe.id')
    cooking_time = serializers.CharField(read_only=True,
                                         source='recipe.cooking_time')
    name = serializers.CharField(read_only=True, source='recipe.name')
    image = serializers.CharField(read_only=True, source='recipe.image')

    class Meta:
        model = Cart
        fields = ('id', 'name', 'image', 'cooking_time')
