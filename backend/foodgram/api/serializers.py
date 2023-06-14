from djoser.serializers import UserSerializer
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription, User

from .custom_fields import Base64ImageField
from .utils import create_ingredient


class UserSignUpSerializer(UserSerializer):
    """Сериализатор, используемый для регистрации пользователя"""
    password = serializers.CharField(
        write_only=True,
        required=True
    )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        """Статус подписки на автора."""
        user_id = self.context.get('request').user.id
        return Subscription.objects.filter(
            author=obj.id, user=user_id).exists()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')


class UserSubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор, используемый для подписки на автора"""
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        request = self.context.get('request')
        if request.user == data['author']:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return UserGetRetrieveSerializer(
            instance.author, context={'request': request}
        ).data


class UserGetRetrieveSerializer(UserSerializer):
    """Сериализатор, используемый для получения информации об авторе"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and Subscription.objects.filter(
                    user=request.user, author=obj).exists())


class TagSerialiser(serializers.ModelSerializer):
    """Сериализатор тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'colour', 'slug')


class IngredientCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов, используемый
    для добавления рецепта"""
    amount = serializers.IntegerField()
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IngredientGetRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов, используемый
    для выдачи ингредиента/списка ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта, используемый для создания/изменения рецепта"""
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    ingredients = IngredientCreateSerializer(
        many=True, source='recipeingredient'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('tags', 'author',
                  'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def create(self, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_ingredient(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipeingredient')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        create_ingredient(ingredients, instance)
        return instance

    def validate(self, data):
        ingredients_list = []
        for ingredient in data.get('recipeingredient'):
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть меньше 1'
                )
            ingredients_list.append(ingredient.get('id'))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'В рецепт нельзя добавить одинаковые ингредиенты!'
                'Увеличьте количество!'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        return RecipeGetRetrieveSerializer(
            instance,
            context={'request': request}
        ).data


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о списке ингредиентов
    и их количестве, используемый для получения информации о рецепте"""
    id = serializers.IntegerField(source='ingredient.id', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeGetRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта, используемый для выдачи информации о рецепте"""
    tags = TagSerialiser(many=True, read_only=True)
    author = UserGetRetrieveSerializer(read_only=True)
    ingredients = RecipeIngredientGetSerializer(
        many=True, read_only=True,
        source='recipeingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Favourite.objects.filter(
                user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated
                and ShoppingCart.objects.filter(
                    user=request.user, recipe=obj).exists())


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор краткой версии рецепта"""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__',)


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта, используемый для
    добавления и удаления рецепта в корзину покупок"""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в список покупок'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class FavouriteSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта, используемый для
    добавления и удаления рецепта в избранное"""

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favourite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в избранное'
            )
        ]

    def to_representation(self, instance):
        request = self.context.get('request')
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': request}
        ).data


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Cериализатор, используемый для получения
    списка авторов, на которых подписан пользователь."""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return (
            self.context.get('request').user.is_authenticated
            and Subscription.objects.filter(user=self.context['request'].user,
                                            author=obj).exists()
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        return ShortRecipeSerializer(recipes, many=True,
                                     context={'request': request}).data
