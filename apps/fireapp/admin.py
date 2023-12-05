from django.contrib import admin
from .models import Sensor, ExtendedUser


admin.site.register(Sensor)
admin.site.register(ExtendedUser)
