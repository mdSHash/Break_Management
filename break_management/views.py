from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BreakSlot, BreakSettings, create_break_slots
from .forms import CustomUserCreationForm, BreakSettingsForm
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from datetime import timedelta
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    # Retrieve all break slots associated with the logged-in user's team or the user themselves
    if request.user.is_manager:
        slots = BreakSlot.objects.all()
    else:
        slots = BreakSlot.objects.filter(agent=request.user)

    # Separate available and taken slots
    available_slots = slots.filter(is_taken=False)
    taken_slots = slots.filter(is_taken=True)

    # Debug: Print available and taken slots
    print("Available slots:", available_slots)
    print("Taken slots:", taken_slots)

    return render(request, 'dashboard.html', {
        'available_slots': available_slots,
        'taken_slots': taken_slots
    })


@login_required
def request_break(request, slot_id):
    slot = get_object_or_404(BreakSlot, id=slot_id, is_taken=False)
    agent = request.user

    # Check if the agent has enough remaining break time
    if agent.remaining_break_time() < timedelta(minutes=15):
        messages.error(request, "You have finished your daily break time.")
        return redirect('dashboard')

    # Mark the slot as taken
    slot.is_taken = True
    slot.agent = agent
    slot.save()

    # Update the agent's total break time
    agent.total_break_time_taken += timedelta(minutes=15)
    agent.save()

    return redirect('dashboard')


@login_required
def manage_settings(request):
    settings, created = BreakSettings.objects.get_or_create(manager=request.user)

    if request.method == 'POST':
        form = BreakSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            create_break_slots(request.user)  # Create break slots
            return redirect('dashboard')
    else:
        form = BreakSettingsForm(instance=settings)

    return render(request, 'break_management/manage_settings.html', {'form': form})
