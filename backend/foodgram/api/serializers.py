from api.models import Ingredient, Recipe, Tag, IngredientInRecipe
from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from . import fields

User = get_user_model()

VALIDATION_ERROR_TAGS = 'Проверьте правильность выбора тэгов.'
VALIDATION_ERROR_INGREDIENTS = 'Проверьте правильность выбора ингредиентов.'


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


class IngredientInRecipeWriteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(min_value=0)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    color = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = '__all__'
    
    def get_color(self, obj):
        value = hex(obj.color)[2:].upper()
        return '#' + '0'*(6-len(value)) + value


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserReadSerializer()
    ingredients = IngredientInRecipeSerializer(source='ingredientinrecipe_set',
                                               read_only=True,
                                               many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = '__all__'


class RecipeReadPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    tags = serializers.ListField(child=serializers.IntegerField(min_value=0))
    image = fields.Base64ImageField()
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_ingredients(self, value):
        ids = [ingredient['id'] for ingredient in value]
        if Ingredient.objects.filter(id__in=ids).count() < len(value):
            raise serializers.ValidationError(VALIDATION_ERROR_INGREDIENTS)
        return value

    def validate_tags(self, value):
        if Tag.objects.filter(id__in=value).count() < len(value):
            raise serializers.ValidationError(VALIDATION_ERROR_TAGS)
        return value

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            **dict((key, validated_data[key])
                   for key in validated_data
                   if key not in ('ingredients', 'tags'))
        )
        # Ingredients
        for ingredient, amount in (
            (ingredient['id'], {'amount': ingredient['amount']})
            for ingredient in validated_data['ingredients']
        ):
            recipe.ingredients.add(ingredient, through_defaults=amount)
        # Tags
        recipe.tags.add(*validated_data['tags'])
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        for ingredient, amount in (
            (ingredient['id'], {'amount': ingredient['amount']})
            for ingredient in validated_data['ingredients']
        ):
            instance.ingredients.add(ingredient, through_defaults=amount)
        # Tags
        instance.tags.clear()
        instance.tags.add(*validated_data['tags'])
        return super().update(instance, dict((key, value)
                   for key,value in validated_data.items()
                   if key not in ('ingredients', 'tags')))
        




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
        return RecipeReadPartialSerializer(
            obj.recipes.all()[:self.get_recipe_count(obj)],
            many=True,
        ).data
        

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 
                  'is_subscribed', 'recipes', 'recipe_count')
