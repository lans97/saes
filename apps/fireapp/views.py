from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Sensor
from .forms import SignUpForm, SensorForm

import matplotlib.pyplot as plt
from io import BytesIO
import base64

from firebase_admin import db

def landing(request):
    return render(request, 'landing/home.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'landing/login.html', { 'form': form })

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing-login')
    else:
        form = SignUpForm()
    return render(request, 'landing/register.html', { 'form': form })

@login_required
def home(request):
    return render(request, 'fireapp/home.html')

@login_required
def profile_view(request):
    return render(request, 'fireapp/profile.html')

@login_required
def settings_view(request):
    return render(request, 'fireapp/settings.html')

@login_required
def sensors_view(request):
    context = {}
    user = request.user
    user_sensors = user.sensor_set.all()
    context['user'] = user
    context['user_sensors'] = user_sensors
    if request.method == "POST":
        if 'delete' in request.POST:
            pk = request.POST.get('delete')
            sensor = Sensor.objects.get(sensor_id=pk)
            sensor.delete()

    return render(request, 'fireapp/sensors.html', context)

@login_required
def add_sensor_view(request):
    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)
            sensor.user = request.user
            sensor.save()
            return redirect('sensors')
    else:
        form = SensorForm()

    return render(request, 'fireapp/add-sensor.html', { 'form': form })

@login_required
def dashboard_view(request, sensor_id):
    ref = db.reference('/')
    ref.set(value)
    context = {}
    context['sensor_id'] = sensor_id
    return render(request, 'fireapp/dashboard.html', context)

def logout_view(request):
    logout(request)
    next_url = request.POST.get('next') or request.GET.get('next') or 'landing-home'
    return redirect(next_url)

def plot_ex(request):
    # Your data for the plot
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 15, 25, 30]

    # Create the plot
    plt.plot(x, y)
    plt.xlabel('X-axis label')
    plt.ylabel('Y-axis label')
    plt.title('My Plot')

    # Save the plot to a BytesIO object
    image_stream = BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)
    plt.close()

    # Convert the BytesIO object to a base64-encoded string
    image_base64 = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    # Pass the base64 string to the template
    context = {'image_base64': image_base64}
    return render(request, 'fireapp/example.html', context)
