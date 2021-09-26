from django.contrib import admin

from .models import IngredientInRecipe, User, Subscription, Ingredient, Tag, Recipe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('email', 'username')


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
    list_display = ('name', 'author',)
    inlines = (IngredientInlineAdmin,)
    search_fields = ('author', 'name', 'text')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
