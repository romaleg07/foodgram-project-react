from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorites, Ingredients, RecipeIngredients, Recipes,
                            ShoppingCart, Tags)
from rest_framework import serializers
from users.models import Follow, User


class UsersSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username',
                  'first_name', 'last_name', 'password',
                  'is_subscribed')
        extra_kwargs = {"password": {"write_only": True}}

    '''
    Не знаю почему, но без этого кода пароль в бд
    записывается в виде строки без шифрования
    отсюда не работают проверки на пароль или выдача токенов
    в интернете нашел это решение
    '''
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribed.filter(user=request.user).exists()


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    new_password = serializers.CharField(max_length=128, required=True)
    current_password = serializers.CharField(max_length=128, required=True)

    def validate_current_password(self, value):
        user = self.context.get('request').user
        if not user.check_password(value):
            raise serializers.ValidationError("Wrong password")
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = '__all__'


class ResipeIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredients
        fields = '__all__'


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all(),
        source='ingredient')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    # ingredients = ResipeIngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        print(object.__dict__)
        return object.favorite_recipe.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.shopping_cart.filter(user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UsersSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = AddIngredientSerializer(many=True)

    class Meta:
        model = Recipes
        fields = '__all__'

    def get_ingredients(self, recipe, ingredients):
        RecipeIngredients.objects.bulk_create(
            RecipeIngredients(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipes.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.get_ingredients(recipe, ingredients)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredients.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipes
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = ('user', 'recipe',)

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def to_representation(self, instance):
        return RecipeShortSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('id', 'author', 'user')
        read_only_fields = fields

    def validate(self, data):
        author = self.context['author']
        user = self.context['request'].user
        if (
            author == user
            or Follow.objects.filter(
                author=author,
                user=user
            ).exists()
        ):
            raise serializers.ValidationError(
                'Нельзя подписаться на этого пользователя!'
            )
        return data


class UserIncludeSerializer(UsersSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.user.count()

    def get_recipes(self, obj):
        recipes_limit = (
            self._context['request'].query_params.get('recipes_limit', False)
        )
        recipes = obj.user.all()
        if recipes_limit:
            recipes = recipes[:abs(int(recipes_limit))]

        serializer = RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context
        )
        return serializer.data
