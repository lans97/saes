from django.shortcuts import render
from .models import SampleData
import firebase_admin

# Create your views here.

def display_sample_data(request):
    sample_data = SampleData.objects.all()
    return render(request, 'fireapp/sample_data.html', {'sample_data': sample_data})