# management/commands/generate_sample_foods.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dating.models import UserProfile, FoodProfile
from dating.views import generate_food_profiles

class Command(BaseCommand):
    help = 'Generate sample food profiles for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=20, help='Number of food profiles to generate')
        parser.add_argument('--user', type=str, help='Username to generate foods for')

    def handle(self, *args, **options):
        count = options['count']
        username = options.get('user')
        
        if username:
            try:
                user = User.objects.get(username=username)
                user_profile = UserProfile.objects.get(user=user)
            except (User.DoesNotExist, UserProfile.DoesNotExist):
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" or their profile not found')
                )
                return
        else:
            # Create a default user profile for generation
            user, created = User.objects.get_or_create(
                username='food_generator',
                defaults={'email': 'generator@example.com'}
            )
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'diet_preferences': 'omnivore',
                    'daily_calorie_goal': 2000,
                    'activity_level': 'moderately_active',
                    'favorite_cuisines': 'Italian, Mexican, Asian, American, Mediterranean'
                }
            )

        self.stdout.write(f'Generating {count} food profiles...')
        
        try:
            generate_food_profiles(user_profile, count)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated {count} food profiles!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error generating food profiles: {str(e)}')
            )