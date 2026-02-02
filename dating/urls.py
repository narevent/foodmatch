# urls.py
from django.urls import path
from . import views

app_name = 'dating'

urlpatterns = [
    path('', views.discover, name='discover'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('setup-profile/', views.setup_profile, name='setup_profile'),
    path('discover/', views.discover, name='discover'),
    path('swipe/', views.swipe_food, name='swipe_food'),
    path('matches/', views.matches, name='matches'),
    path('add-to-meal-plan/<int:match_id>/', views.add_to_meal_plan, name='add_to_meal_plan'),
]