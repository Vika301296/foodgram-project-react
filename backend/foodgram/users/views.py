from django.shortcuts import get_object_or_404
from recipes.serializers import SubscriptionsSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription, User
from .serializers import UserSubscribeSerializer


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    http_method_names = ['post', 'delete']

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk):
        user = request.user
        author = User.objects.get(id=pk)

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
