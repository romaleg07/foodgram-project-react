from api.serializers import (FavoriteSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             RecipeWriteSerializer, ShoppingCartSerializer,
                             TagSerializer)
from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny
from rest_framework.response import Response
from users.models import User

from . import generate_cart
from .filters import RecipeFilter
from .mixins import ListRetrieveViewSet
from .models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                     ShoppingCart, Tags)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


@action(detail=False, methods=['get'])
class TagsViewSet(ListRetrieveViewSet):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    model = Tags
    queryset = Tags.objects.all()
    pagination_class = None


@action(detail=False, methods=['get'])
class IngredientViewSet(ListRetrieveViewSet):
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    model = Ingredients
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredients.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            return queryset.filter(name__startswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Recipes.objects.all()
    permission_classes = (IsAuthorOrReadOnly | IsAdminOrReadOnly,)
    model = Recipes
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Recipes.objects.all()

        user_favorited = Favorites.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )
        user_shoppingcart = ShoppingCart.objects.filter(
            recipe=OuterRef('pk'),
            user=self.request.user,
        )

        return Recipes.objects.annotate(
            is_favorited=Exists(user_favorited)
        ).annotate(
            is_in_shopping_cart=Exists(user_shoppingcart)
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    @staticmethod
    def add_to(pk, request, serializer):
        data = {
            'user': request.user.id,
            'recipe': pk
        }
        user = get_object_or_404(User, pk=request.user.id)
        recipe = get_object_or_404(Recipes, pk=pk)
        serializer = serializer(
            data=data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=user,
            recipe=recipe
        )
        response = RecipeShortSerializer(
            Recipes.objects.get(id=pk), context={'request': request}
        )
        return Response(
            response.data, status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def delete_from(pk, request, model):
        recipe = get_object_or_404(Recipes, pk=pk)
        get_object_or_404(model, recipe=recipe, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk):
        return self.add_to(pk, request, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        return self.delete_from(pk, request, Favorites)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk):
        return self.add_to(pk, request, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        return self.delete_from(pk, request, ShoppingCart)

    @action(detail=False)
    def download_shopping_cart(self, request):
        recipes = Recipes.objects.filter(shoppingcart__user=self.request.user)
        ingredients_to_recipes = RecipeIngredients.objects.filter(
            recipe__in=recipes
        )
        pdf = generate_cart.generate(ingredients_to_recipes)
        return FileResponse(
            pdf,
            as_attachment=True,
            filename='shopping_cart.pdf')
