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
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_taken = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Break Slot for {self.agent} from {self.start_time} to {self.end_time}"

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
    start_time = datetime.combine(timezone.now().date(), settings.working_hours_start)
    end_time = datetime.combine(timezone.now().date(), settings.working_hours_end)
    slot_duration = timedelta(minutes=15)
    
    current_time = start_time
    while current_time < end_time:
        BreakSlot.objects.create(
            agent=manager,
            start_time=current_time,
            end_time=current_time + slot_duration,
            is_taken=False
        )
        current_time += slot_duration
