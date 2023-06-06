from djoser.serializers import UserSerializer
# from recipes.serializers import ShortRecipeSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Subscription, User


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
        if (request.user.is_authenticated
                and Subscription.objects.filter(
                    user=request.user, author=obj).exists()):
            return True
        return False


# class UserSubscribeToRepresentationSerializer(UserGetRetrieveSerializer):
#     """"Сериализатор, используемый для получения информации
#     о подписках пользователя."""
#     is_subscribed = serializers.SerializerMethodField()
#     recipes = serializers.SerializerMethodField()
#     recipes_count = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name',
#                   'last_name', 'is_subscribed', 'recipes', 'recipes_count')
#         read_only_fields = ('email', 'username', 'first_name', 'last_name',
#                             'is_subscribed', 'recipes', 'recipes_count')

#     def get_recipes(self, obj):
#         request = self.context.get('request')
#         return ShortRecipeSerializer(recipes, many=True,
#                                      context={'request': request}).data

#     def get_recipes_count(self, obj):
#         return obj.recipes.count()
