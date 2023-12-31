from django.db import models
from django.contrib.auth.models import User

class Sensor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sensor_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    registration_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    # Add additional variables to configure sensor behavior
    # For example:
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ExtendedUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    title = models.CharField(max_length=25, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="static/img/userProfile/", null=True, blank=True)
    
    def __str__(self):
        return self.user.username