from django.db import models

# Create your models here.

class SampleData(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=200)