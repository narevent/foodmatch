# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime, timedelta
import json
import random
from g4f.client import Client
from .models import UserProfile, FoodProfile, Match, WeeklyFoodLog, CustomUser
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dating:discover')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dating:setup_profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dating/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dating:discover')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # AuthenticationForm uses 'username' field
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                # Check if profile is completed
                try:
                    profile = user.userprofile
                    if not profile.profile_completed:
                        return redirect('dating:setup_profile')
                except UserProfile.DoesNotExist:
                    return redirect('dating:setup_profile')
                return redirect('dating:discover')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    return render(request, 'dating/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('dating:login')

@login_required
def setup_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.profile_completed = True
            profile.save()
            messages.success(request, 'Profile setup completed!')
            return redirect('dating:discover')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'dating/setup_profile.html', {'form': form, 'profile': user_profile})

@login_required
def discover(request):
    # Check if profile is completed
    try:
        user_profile = request.user.userprofile
        if not user_profile.profile_completed:
            return redirect('dating:setup_profile')
    except UserProfile.DoesNotExist:
        return redirect('dating:setup_profile')
    
    # Get foods user hasn't seen yet
    seen_food_ids = Match.objects.filter(user=request.user).values_list('food_profile_id', flat=True)
    available_foods = FoodProfile.objects.filter(
        diet_compatibility=user_profile.diet_preferences
    ).exclude(id__in=seen_food_ids)
    
    # If no foods available, generate new ones
    if not available_foods.exists():
        generate_food_profiles(user_profile)
        available_foods = FoodProfile.objects.filter(
            diet_compatibility=user_profile.diet_preferences
        ).exclude(id__in=seen_food_ids)
    
    current_food = available_foods.first() if available_foods.exists() else None
    
    return render(request, 'dating/discover.html', {
        'current_food': current_food,
        'user_profile': user_profile
    })

@csrf_exempt
@login_required
def swipe_food(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        food_id = data.get('food_id')
        action = data.get('action')  # 'like' or 'pass'
        
        food_profile = get_object_or_404(FoodProfile, id=food_id)
        
        # Create or update match
        match, created = Match.objects.get_or_create(
            user=request.user,
            food_profile=food_profile,
            defaults={'user_liked': action == 'like'}
        )
        
        if not created:
            match.user_liked = action == 'like'
            match.save()
        
        # If user liked, check if food likes back
        if action == 'like':
            food_likes_back = calculate_food_preference(request.user, food_profile)
            match.food_liked = food_likes_back
            match.save()
            
            if food_likes_back:
                return JsonResponse({
                    'status': 'mutual_match',
                    'message': f"It's a match! {food_profile.name} likes you back!"
                })
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'})

@login_required
def matches(request):
    mutual_matches = Match.objects.filter(
        user=request.user,
        user_liked=True,
        food_liked=True
    ).select_related('food_profile')
    
    return render(request, 'dating/matches.html', {'matches': mutual_matches})

@login_required
def add_to_meal_plan(request, match_id):
    match = get_object_or_404(Match, id=match_id, user=request.user)
    
    if request.method == 'POST':
        meal_type = request.POST.get('meal_type')
        date_str = request.POST.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        WeeklyFoodLog.objects.get_or_create(
            user=request.user,
            food_profile=match.food_profile,
            date_consumed=date,
            defaults={'meal_type': meal_type}
        )
        
        return redirect('dating:matches')
    
    return render(request, 'dating/add_to_meal_plan.html', {'match': match})

def generate_food_profiles(user_profile, count=10):
    """Generate new food profiles using AI"""
    client = Client()
    
    cuisines = user_profile.get_cuisines_list() or ['Italian', 'Mexican', 'Asian', 'American', 'Mediterranean']
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for _ in range(count):
        try:
            # Generate food description
            cuisine = random.choice(cuisines)
            meal_type = random.choice(meal_types)
            
            prompt = f"""Create a {user_profile.diet_preferences} {meal_type} recipe from {cuisine} cuisine. 
            Avoid these allergies: {', '.join(user_profile.get_allergies_list()) if user_profile.get_allergies_list() else 'none'}.
            Target calories: {user_profile.daily_calorie_goal // 4} calories.
            
            Respond in this exact JSON format:
            {{
                "name": "Recipe Name",
                "description": "Brief appetizing description",
                "calories": 450,
                "ingredients": "ingredient1, ingredient2, ingredient3"
            }}"""
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional chef creating recipes. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                web_search=False
            )
            
            # Parse AI response
            try:
                food_data = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                food_data = {
                    "name": f"{cuisine} {meal_type.title()}",
                    "description": f"A delicious {cuisine} {meal_type}",
                    "calories": random.randint(200, 800),
                    "ingredients": "fresh ingredients"
                }
            
            # Generate food image
            image_prompt = f"professional food photography of {food_data['name']}, {food_data['description']}, appetizing, well-lit, restaurant quality"
            
            try:
                image_response = client.images.generate(
                    model="flux",
                    prompt=image_prompt,
                    response_format="url"
                )
                image_url = image_response.data[0].url
            except:
                image_url = ""
            
            # Create food profile
            FoodProfile.objects.create(
                name=food_data['name'],
                description=food_data['description'],
                calories=food_data['calories'],
                meal_type=meal_type,
                cuisine_type=cuisine,
                diet_compatibility=user_profile.diet_preferences,
                ingredients=food_data['ingredients'],
                image_url=image_url,
                generated_prompt=prompt,
                generation_successful=True
            )
            
        except Exception as e:
            print(f"Error generating food profile: {e}")
            continue

def calculate_food_preference(user, food_profile):
    """Calculate if a food profile would 'like' the user back based on variety"""
    # Get user's food log for the past week
    week_ago = timezone.now().date() - timedelta(days=7)
    recent_foods = WeeklyFoodLog.objects.filter(
        user=user,
        date_consumed__gte=week_ago
    ).select_related('food_profile')
    
    # Calculate variety score
    unique_cuisines = set(log.food_profile.cuisine_type for log in recent_foods)
    unique_meal_types = set(log.food_profile.meal_type for log in recent_foods)
    
    variety_score = len(unique_cuisines) + len(unique_meal_types)
    
    # Food likes users with more variety (higher chance with more variety)
    base_chance = 0.3  # 30% base chance
    variety_bonus = min(variety_score * 0.1, 0.5)  # Up to 50% bonus
    
    # Check if user hasn't had this cuisine recently
    if food_profile.cuisine_type not in unique_cuisines:
        variety_bonus += 0.2
    
    final_chance = min(base_chance + variety_bonus, 0.9)  # Max 90% chance
    
    return random.random() < final_chance