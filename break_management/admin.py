from django.contrib import admin
from .models import CustomUser, BreakSlot, BreakSettings

admin.site.register(CustomUser)
admin.site.register(BreakSlot)
admin.site.register(BreakSettings)
