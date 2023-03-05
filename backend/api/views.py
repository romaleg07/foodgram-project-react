from django.db.models import Exists, OuterRef
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.serializers import (ChangePasswordSerializer, FavoriteSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             RecipeWriteSerializer, ShoppingCartSerializer,
                             TagSerializer, UserIncludeSerializer,
                             UsersSerializer)
from foodgram.core.pagination import PageNumberLimitPagination
from recipes import generate_cart
from recipes.filters import RecipeFilter
from recipes.mixins import ListRetrieveViewSet
from recipes.models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                            ShoppingCart, Tags)
from users.models import Follow, User


class UsersViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    pagination_class = PageNumberLimitPagination
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ['get', 'post', 'delete', 'head']

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        serializer = FollowSerializer(
            context={
                'request': request,
                'author': author
            },
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            user=self.request.user,
            author=author
        )
        headers = self.get_success_headers(serializer.data)
        response = UserIncludeSerializer(
            author, context={'request': request}
        )
        return Response(
            response.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        author = get_object_or_404(self.queryset, pk=pk)
        get_object_or_404(
            Follow, author=author, user=self.request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        subscribtions = self.queryset.filter(
            subscribed__user=self.request.user
        )
        page = self.paginate_queryset(subscribtions)

        if not page:
            serializer = UserIncludeSerializer(
                subscribtions, many=True, context={'request': request}
            )
            return Response(serializer.data)

        serializer = UserIncludeSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@action(detail=False, methods=['get'])
class MeViewSet(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UsersSerializer
    pagination_class = None

    def get_object(self):
        username = self.request.user.username
        return get_object_or_404(User, username=username)

    def perform_update(self, serializer):
        serializer.save()


class SetNewPasswordUser(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        return self.request.user

    def create(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()

            return Response(status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
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
        recipes = Recipes.objects.filter(shopping_cart__user=self.request.user)
        ingredients_to_recipes = RecipeIngredients.objects.filter(
            recipe__in=recipes
        )
        pdf = generate_cart.generate(ingredients_to_recipes)
        return FileResponse(
            pdf,
            as_attachment=True,
            filename='shopping_cart.pdf')
