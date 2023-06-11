from datetime import datetime as dt

from django.shortcuts import HttpResponse
from rest_framework import response, status
from rest_framework.generics import get_object_or_404

from ..recipes.models import Recipe, RecipeIngredient

# Не очень поняла тут про время. Ты мне отправил ссылку на кдокументацию
# из Django, где используется тот же datetime. (Настройки в settings я
# проверила, определение timezone у меня работает.)
# Еще я увидела, что там упоминается timezone, но он используется для времени,
# которое здесь не задействовано.
# В общем, не мог бы ты, пожалуйста, пояснить этот пункт?:)


def list_ingredients(self, request, ingredients):
    user = self.request.user
    filename = f'{user.username}_shopping_list.txt'

    today = dt.today()
    shopping_list = (
        f'Список покупок пользователя: {user.username}\n\n'
        f'Дата: {today:%Y-%m-%d}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    shopping_list += f'\n\nFoodgram ({today:%Y})'

    response = HttpResponse(
        shopping_list, content_type='text.txt; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def post_or_delete(request, pk, model, serializer_name):
    user = request.user
    data = {'user': user.id,
            'recipe': pk}
    serializer = serializer_name(data=data, context={'request': request})
    if request.method == 'POST':
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data,
                                 status=status.HTTP_201_CREATED)
    get_object_or_404(
        model, user=user, recipe=get_object_or_404(Recipe, id=pk)
    ).delete()
    return response.Response(status=status.HTTP_204_NO_CONTENT)


def create_ingredient(ingredients, recipe):
    ingredient_list = []
    for ingredient in ingredients:
        current_ingredient = ingredient.id
        amount = ingredient.get('amount')
        ingredient_list.append(
            RecipeIngredient(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    RecipeIngredient.objects.bulk_create(ingredient_list)
