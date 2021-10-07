from django.contrib import admin

from .models import (
    Ingredient, IngredientInRecipe, Recipe, Subscription, Tag, User,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')
    list_filter = ('email', 'username')
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
    readonly_fields = ('is_favorited',)
    inlines = (IngredientInlineAdmin,)
    search_fields = ('author__username', 'name', 'text', 'tags__slug')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)

    @admin.display(description='Число добавлений в избранное')
    def is_favorited(self, obj):
        return obj.users_have_in_favorite.count()


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
