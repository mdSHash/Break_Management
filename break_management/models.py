from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta, datetime
from django.utils import timezone

class CustomUser(AbstractUser):
    is_manager = models.BooleanField(default=False)
    team_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    total_break_time_taken = models.DurationField(default=timedelta())

    def remaining_break_time(self):
        max_break_time = timedelta(minutes=90)  # 1.5 hours
        return max_break_time - self.total_break_time_taken


class BreakSlot(models.Model):
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  # Initially no agent
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_taken = models.BooleanField(default=False)
    
    def __str__(self):
        agent_name = self.agent.username if self.agent else "Available"
        return f"Break Slot from {self.start_time} to {self.end_time} ({agent_name})"


class BreakSettings(models.Model):
    manager = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    break_slots_per_hour = models.IntegerField(default=5)  # 5 slots of 15 minutes each
    working_hours_start = models.TimeField()
    working_hours_end = models.TimeField()
    is_rush_hour = models.BooleanField(default=False)
    rush_hour_start = models.TimeField(null=True, blank=True)
    rush_hour_end = models.TimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Settings for {self.manager.team_name}"

def initialize_default_break_settings(manager):
    from django.db import IntegrityError

    # Default settings
    default_settings = {
        'working_hours_start': '15:00:00',
        'working_hours_end': '03:00:00',
        'break_slots_per_hour': 2,
    }

    # Create default settings if they do not exist
    try:
        BreakSettings.objects.get(manager=manager)  # Check if settings already exist
    except BreakSettings.DoesNotExist:
        BreakSettings.objects.create(
            manager=manager,
            working_hours_start=default_settings['working_hours_start'],
            working_hours_end=default_settings['working_hours_end'],
            break_slots_per_hour=default_settings['break_slots_per_hour'],
        )
        print("Default break settings created.")

def create_break_slots(manager):
    settings = BreakSettings.objects.get(manager=manager)

    # Calculate the start and end of the working hours
    start_time = datetime.combine(timezone.now().date(), settings.working_hours_start)
    end_time = datetime.combine(timezone.now().date(), settings.working_hours_end)

    # If end_time is before start_time, it means it goes past midnight
    if end_time < start_time:
        end_time += timedelta(days=1)  # Move end_time to the next day

    # Slot configuration
    slot_duration = timedelta(minutes=15)  # Each break slot is 15 minutes
    available_slots_per_time = settings.break_slots_per_hour  # Number of available slots set by the manager
    
    # Clear previous slots for the day
    BreakSlot.objects.filter(start_time__date=timezone.now().date()).delete()

    current_time = start_time

    while current_time < end_time:  # Changed from != to <
        # Create fixed number of slots for the current time
        for _ in range(available_slots_per_time):
            # Create break slot
            slot = BreakSlot.objects.create(
                start_time=current_time,
                end_time=current_time + slot_duration,
                is_taken=False
            )
            print(f"Created slot: {slot.start_time} to {slot.end_time}")  # Debug output

        current_time += slot_duration  # Move to the next time interval

