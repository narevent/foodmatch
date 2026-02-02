# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile, CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500',
            'placeholder': 'Password'
        })
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['diet_preferences', 'allergies', 'daily_calorie_goal', 'activity_level', 'favorite_cuisines']
        widgets = {
            'diet_preferences': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'e.g., nuts, dairy, gluten',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500'
            }),
            'favorite_cuisines': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'e.g., Italian, Mexican, Asian',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500'
            }),
            'daily_calorie_goal': forms.NumberInput(attrs={
                'min': 1000, 
                'max': 5000,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500'
            }),
            'activity_level': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-pink-500'
            }),
        }