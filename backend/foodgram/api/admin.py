from django.contrib import admin

from .models import (
    Ingredient, IngredientInRecipe, Recipe, Subscription, Tag, User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    filter_horizontal = ('shopping_cart_recipes', 'favorite_recipes',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('author', 'subscriber')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientInlineAdmin(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date')
    inlines = (IngredientInlineAdmin,)
    search_fields = ('author', 'name', 'text')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
