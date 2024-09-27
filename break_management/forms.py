from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, BreakSettings

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'team_name', 'is_manager']

class BreakSettingsForm(forms.ModelForm):
    class Meta:
        model = BreakSettings
        fields = ['break_slots_per_hour', 'working_hours_start', 'working_hours_end', 'is_rush_hour', 'rush_hour_start', 'rush_hour_end']
