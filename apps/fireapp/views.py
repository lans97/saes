from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Sensor
from .forms import SignUpForm, SensorForm

import plotly.express as px
from django.http import JsonResponse
import pandas as pd
from datetime import datetime

from firebase_admin import db

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')

    return render(request, 'landing/home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
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
    if request.user.is_authenticated:
        return redirect('home')
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
    ref = db.reference('/sensors/' + sensor_id + "/data")
    context = {}
    context['sensor_id'] = sensor_id

    options = {"Humedad": 'hum', "Intensidad Luminosa": 'luz', "Sonido": 'sonido', "Temperatura": 'temp', "Ubicación": 'loc'}
    units = {"Humedad": '[]', "Intensidad Luminosa": '[]', "Sonido": '[dB]', "Temperatura": '[°C]', "Ubicación": ''}
    current_var = options["Temperatura"]
    current_key = "Temperatura"
    if request.method == 'POST':
        current_key = request.POST.get('setvar')
        current_var = options[current_key]

    sensor_data = ref.get()

    if current_var == "loc":
        df = pd.DataFrame(sensor_data)
        fig = px.scatter_geo(df, lat='lat', lon='lng', title='Sensor Map', projection='natural earth')

    else:
        tiempo = [datetime(2000, 1, 1, entry['hora'], entry['minuto'], entry['segundo']) for entry in sensor_data]
        df = pd.DataFrame({'Tiempo': tiempo, current_key+" "+units[current_key]: [entry[current_var] for entry in sensor_data]})



        # Plotly
        fig = px.scatter(df, x='Tiempo', y=current_key+" "+units[current_key], title=sensor_id)

    context['vars_list'] = list(options.keys())


    plot_json = fig.to_json()
    context['plot_json'] = plot_json

    return render(request, 'fireapp/dashboard.html', context)

def logout_view(request):
    logout(request)
    next_url = request.POST.get('next') or request.GET.get('next') or 'landing-home'
    return redirect(next_url)

