from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BreakSlot, BreakSettings, create_break_slots, CustomUser, initialize_default_break_settings
from .forms import CustomUserCreationForm, BreakSettingsForm
from django.contrib.auth import login as auth_login
from datetime import timedelta, datetime
from django.contrib import messages
from django.utils import timezone  # Correct import



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
    # Ensure BreakSettings exist for the manager
    if request.user.is_manager:
        initialize_default_break_settings(request.user)

    # Check if break slots exist for today or until the end of working hours
    slots_exist = BreakSlot.objects.filter(
        start_time__date=timezone.now().date()
    ).exists() or BreakSlot.objects.filter(
        start_time__date=timezone.now().date() + timedelta(days=1),
        start_time__gte=datetime.combine(timezone.now().date(), timezone.now().time())
    ).exists()

    if not slots_exist:
        create_break_slots(request.user)  # Automatically create slots if none exist

    # Retrieve all break slots for the user's team
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    slots = BreakSlot.objects.filter(
        start_time__date__in=[today, tomorrow]
    )

    # Separate available and taken slots
    available_slots = slots.filter(is_taken=False)
    taken_slots = slots.filter(is_taken=True)

    print(f"Available slots count: {available_slots.count()}")  # Debugging output
    print(f"Taken slots count: {taken_slots.count()}")  # Debugging output

    return render(request, 'dashboard.html', {
        'available_slots': available_slots,
        'taken_slots': taken_slots
    })




@login_required
def request_break(request, slot_id):
    slot = get_object_or_404(BreakSlot, id=slot_id, is_taken=False)
    agent = request.user

    # Debug output to check the agent's total break time before taking a break
    print(f"Current total break time taken for {agent.username}: {agent.total_break_time_taken}")

    # Check if the agent has enough remaining break time (90 minutes max)
    if agent.total_break_time_taken >= timedelta(minutes=90):  # 1.5 hours
        messages.error(request, "You have reached your daily break limit.")
        return redirect('dashboard')

    # Mark the slot as taken
    slot.is_taken = True
    slot.agent = agent
    slot.save()

    # Update the agent's total break time
    agent.total_break_time_taken += timedelta(minutes=15)  # Increment by 15 minutes
    agent.save()

    print(f"Updated total break time taken for {agent.username}: {agent.total_break_time_taken}")  # Debug output

    return redirect('dashboard')




@login_required
def manage_settings(request):
    settings, created = BreakSettings.objects.get_or_create(manager=request.user)

    if request.method == 'POST':
        form = BreakSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            create_break_slots(request.user)  # Adjusts break slots after changes
            return redirect('dashboard')
    else:
        form = BreakSettingsForm(instance=settings)

    return render(request, 'break_management/manage_settings.html', {'form': form})


@login_required
def release_break(request, slot_id):
    slot = get_object_or_404(BreakSlot, id=slot_id, is_taken=True)
    if request.user.is_manager:
        slot.is_taken = False
        slot.agent = None
        slot.save()
        messages.success(request, "Break slot released.")
    return redirect('dashboard')


@login_required
def assign_break(request, slot_id):
    if not request.user.is_manager:
        return redirect('dashboard')
    
    slot = get_object_or_404(BreakSlot, id=slot_id, is_taken=False)
    
    if request.method == 'POST':
        agent_username = request.POST.get('agent_username')
        agent = get_object_or_404(CustomUser, username=agent_username, team_name=request.user.team_name)
        
        # Assign the slot to the agent
        slot.is_taken = True
        slot.agent = agent
        slot.save()
        
        # Update agent's total break time
        agent.total_break_time_taken += timedelta(minutes=15)
        agent.save()
        
        messages.success(request, f"Break slot assigned to {agent.username}.")
        return redirect('dashboard')
    
    # If GET request, render a form to select an agent
    agents = CustomUser.objects.filter(team_name=request.user.team_name, is_manager=False)
    return render(request, 'assign_break.html', {'slot': slot, 'agents': agents})


@login_required
def cancel_break(request, slot_id):
    slot = get_object_or_404(BreakSlot, id=slot_id, agent=request.user, is_taken=True)

    # Mark the slot as available again
    slot.is_taken = False
    slot.agent = None
    slot.save()

    # Deduct the break time from the agent's total
    request.user.total_break_time_taken -= timedelta(minutes=15)
    request.user.save()

    messages.success(request, "Your break has been canceled.")
    return redirect('dashboard')
