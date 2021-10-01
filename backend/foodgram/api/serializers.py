from api.models import Ingredient, Recipe, Tag, IngredientInRecipe
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions

User = get_user_model()


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'id',
                  'is_subscribed')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id','name','measurement_unit','amount')


class TagSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = '__all__'
    
    def get_color(self, obj):
        value = hex(obj.color)[2:].upper()
        return '#' + '0'*(6-len(value)) + value


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer()
    ingredients = IngredientInRecipeSerializer(source='ingredientinrecipe_set',
                                               read_only=True,
                                               many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = serializers.SerializerMethodField()

    def get_image(self, value):
        return self.context['request'].build_absolute_uri(value.image.url)
    
    class Meta:
        model = Recipe
        fields = '__all__'


class RecipePartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    def get_recipe_count(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        all = obj.recipes.count()
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            return all
        return limit if 0 <= limit < all else all

    def get_recipes(self, obj):
        return RecipePartialSerializer(
            obj.recipes.all()[:self.get_recipe_count(obj)],
            many=True,
        ).data
        

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 
                  'is_subscribed', 'recipes', 'recipe_count')
