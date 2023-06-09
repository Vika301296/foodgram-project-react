from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription, User
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (FavouriteSerializer, IngredientGetRetrieveSerializer,
                          RecipeCreateSerializer, RecipeGetRetrieveSerializer,
                          ShoppingCartSerializer, SubscriptionsSerializer,
                          TagSerialiser, UserGetRetrieveSerializer,
                          UserSubscribeSerializer)
from .utils import list_ingredients, post_or_delete


class UserViewSet(UserViewSet):

    serializer_class = UserGetRetrieveSerializer

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        user = request.user
        author = User.objects.get(pk=id)

        if self.request.method == 'POST':
            serializer = UserSubscribeSerializer(
                data={'user': user.pk, 'author': author.pk},
                context={"request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        get_object_or_404(Subscription, user=user,
                          author=author).delete()
        return Response({'detail': 'Вы отписаны от пользователя!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False,
            url_path='subscriptions',
            url_name='subscriptions',
            permission_classes=[IsAuthenticated],)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(page, many=True,
                                             context={'request': request})
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение тега/списка тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerialiser
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Получение ингредиента/списка ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientGetRetrieveSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    search_fields = ('^name', )


class RecipeViewSet(viewsets.ModelViewSet):

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    permission_classes = (IsAdminAuthorOrReadOnly, )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetRetrieveSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def shopping_cart(self, request, pk):
        return post_or_delete(request, pk,
                              ShoppingCart, ShoppingCartSerializer)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated, ]
    )
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=self.request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(
            final_amount=Sum('amount'))
        return list_ingredients(self, request, ingredients)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def favorite(self, request, pk):
        return post_or_delete(
            request, pk, Favourite, FavouriteSerializer
        )
