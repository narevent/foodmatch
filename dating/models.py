from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import datetime, timedelta
import json

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    def __str__(self):
        return self.email

class UserProfile(models.Model):
    DIET_CHOICES = [
        ('omnivore', 'Omnivore'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('keto', 'Keto'),
        ('paleo', 'Paleo'),
        ('mediterranean', 'Mediterranean'),
        ('low_carb', 'Low Carb'),
        ('gluten_free', 'Gluten Free'),
    ]
    
    ACTIVITY_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active'),
        ('extremely_active', 'Extremely Active'),
    ]
    
    # Use string reference to avoid circular import issues
    user = models.OneToOneField('dating.CustomUser', on_delete=models.CASCADE)
    diet_preferences = models.CharField(max_length=20, choices=DIET_CHOICES, default='omnivore')
    allergies = models.TextField(blank=True, help_text="Comma-separated list of allergies")
    daily_calorie_goal = models.IntegerField(default=2000)
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='moderately_active')
    favorite_cuisines = models.TextField(blank=True, help_text="Comma-separated list of favorite cuisines")
    profile_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_allergies_list(self):
        return [allergy.strip() for allergy in self.allergies.split(',') if allergy.strip()]
    
    def get_cuisines_list(self):
        return [cuisine.strip() for cuisine in self.favorite_cuisines.split(',') if cuisine.strip()]

class FoodProfile(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('dessert', 'Dessert'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    calories = models.IntegerField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    cuisine_type = models.CharField(max_length=100)
    diet_compatibility = models.CharField(max_length=20, choices=UserProfile.DIET_CHOICES)
    ingredients = models.TextField(help_text="Comma-separated list of main ingredients")
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # AI generation tracking
    generated_prompt = models.TextField(blank=True)
    generation_successful = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
    def get_ingredients_list(self):
        return [ingredient.strip() for ingredient in self.ingredients.split(',') if ingredient.strip()]

class Match(models.Model):
    # Use string reference to avoid circular import issues
    user = models.ForeignKey('dating.CustomUser', on_delete=models.CASCADE)
    food_profile = models.ForeignKey(FoodProfile, on_delete=models.CASCADE)
    user_liked = models.BooleanField(default=False)
    food_liked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'food_profile']
    
    def is_mutual_match(self):
        return self.user_liked and self.food_liked
    
    def __str__(self):
        status = "Mutual Match" if self.is_mutual_match() else "Pending"
        return f"{self.user.username} - {self.food_profile.name} ({status})"

class WeeklyFoodLog(models.Model):
    # Use string reference to avoid circular import issues
    user = models.ForeignKey('dating.CustomUser', on_delete=models.CASCADE)
    food_profile = models.ForeignKey(FoodProfile, on_delete=models.CASCADE)
    date_consumed = models.DateField(default=timezone.now)
    meal_type = models.CharField(max_length=20, choices=FoodProfile.MEAL_TYPES)
    
    class Meta:
        unique_together = ['user', 'food_profile', 'date_consumed']
    
    def __str__(self):
        return f"{self.user.username} ate {self.food_profile.name} on {self.date_consumed}"