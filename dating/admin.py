# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, FoodProfile, Match, WeeklyFoodLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    # Override fieldsets to properly include email
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'diet_preferences', 'daily_calorie_goal', 'activity_level', 'profile_completed']
    list_filter = ['diet_preferences', 'activity_level', 'profile_completed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

@admin.register(FoodProfile)
class FoodProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'cuisine_type', 'calories', 'diet_compatibility', 'generation_successful']
    list_filter = ['meal_type', 'cuisine_type', 'diet_compatibility', 'generation_successful']
    search_fields = ['name', 'description', 'ingredients']
    readonly_fields = ['created_at']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user', 'food_profile', 'user_liked', 'food_liked', 'is_mutual_match', 'created_at']
    list_filter = ['user_liked', 'food_liked', 'created_at']
    search_fields = ['user__username', 'food_profile__name']
    readonly_fields = ['created_at']
    
    def is_mutual_match(self, obj):
        return obj.is_mutual_match()
    is_mutual_match.boolean = True
    is_mutual_match.short_description = 'Mutual Match'

@admin.register(WeeklyFoodLog)
class WeeklyFoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'food_profile', 'date_consumed', 'meal_type']
    list_filter = ['date_consumed', 'meal_type']
    search_fields = ['user__username', 'food_profile__name']
    date_hierarchy = 'date_consumed'