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


def create_break_slots(manager):
    settings = BreakSettings.objects.get(manager=manager)
    
    # Calculate the start and end of the working hours
    start_time = datetime.combine(timezone.now().date(), settings.working_hours_start)
    end_time = datetime.combine(timezone.now().date(), settings.working_hours_end)
    
    # Slot configuration
    slot_duration = timedelta(minutes=15)  # Each break slot is 15 minutes
    available_slots_per_time = settings.break_slots_per_hour  # Number of available slots set by the manager exp = 3
    
    # Clear previous slots for the day
    BreakSlot.objects.filter(start_time__date=timezone.now().date()).delete()

    current_time = start_time

    while current_time < end_time:
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


# def create_break_slots(manager):
#     settings = BreakSettings.objects.get(manager=manager)
    
#     # Calculate the start and end of the working hours
#     start_time = datetime.combine(timezone.now().date(), settings.working_hours_start)
#     end_time = datetime.combine(timezone.now().date(), settings.working_hours_end)
    
#     # Slot configuration
#     slot_duration = timedelta(minutes=15)  # Each break slot is 15 minutes
#     max_daily_breaks = 6  # Maximum of 1.5 hours of break per agent per day (6 slots of 15 min)
    
#     # Clear previous slots for the day
#     BreakSlot.objects.filter(start_time__date=timezone.now().date()).delete()

#     # Fetch all agents in the manager's team
#     agents = CustomUser.objects.filter(team_name=manager.team_name, is_manager=False)

#     current_time = start_time

#     while current_time < end_time:
#         for agent in agents:
#             # Check if the agent has reached their maximum allowed breaks for the day
#             if agent.total_break_time_taken >= timedelta(minutes=90):  # 1.5 hours
#                 continue
            
#             # Create break slot
#             slot = BreakSlot.objects.create(
#                 agent=agent,  # Create for each agent in the team
#                 start_time=current_time,
#                 end_time=current_time + slot_duration,
#                 is_taken=False
#             )
#             print(f"Created slot for {agent.username}: {slot.start_time} to {slot.end_time}")  # Debug output
        
#         current_time += slot_duration