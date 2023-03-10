from django.urls import include, path
from rest_framework import routers

from .views import (IngredientViewSet, MeViewSet, RecipeViewSet,
                    SetNewPasswordUser, TagsViewSet, UsersViewSet)

router = routers.DefaultRouter()
router.register(r'users', UsersViewSet, basename='users')
router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('users/me/', MeViewSet.as_view()),
    path('users/set_password/', SetNewPasswordUser.as_view()),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
