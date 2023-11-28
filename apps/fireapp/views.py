from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Sensor
from .forms import SignUpForm, SensorForm

import plotly.express as px
from django.http import JsonResponse
import pandas as pd
from datetime import datetime, timedelta

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
    ref = db.reference("/sensors/" + sensor_id + "/data")
    context = {}
    context['sensor_id'] = sensor_id

    options = {"Humedad": 'hum', "Intensidad Luminosa": 'luz', "Sonido": 'sonido', "Temperatura": 'temp', "Ubicación": 'loc'}
    units = {"Humedad": '[]', "Intensidad Luminosa": '[]', "Sonido": '[dB]', "Temperatura": '[°C]', "Ubicación": ''}

    current_var = options["Temperatura"]
    current_key = "Temperatura"

    timestart_str = request.session.get('start_time', datetime.now().strftime("%Y%m%d%H%M%S"))
    timeend_str = request.session.get('end_time', datetime.now().strftime("%Y%m%d%H%M%S"))

    timestart = datetime.strptime(timestart_str, "%Y%m%d%H%M%S")
    timeend = datetime.strptime(timeend_str, "%Y%m%d%H%M%S")
    
    if request.method == 'POST':
        if 'setvar' in request.POST:
            current_key = request.POST.get('setvar')
            current_var = options[current_key]
        elif 'update' in request.POST:
            startd = datetime.strptime(request.POST.get('start_date'), "%Y-%m-%d").date()
            endd = datetime.strptime(request.POST.get('end_date'), "%Y-%m-%d").date()
            startt = datetime.strptime(request.POST.get('start_time'), "%H:%M").time()
            endt = datetime.strptime(request.POST.get('end_time'), "%H:%M").time()
            timestart = datetime.combine(startd, startt)
            timeend = datetime.combine(endd, endt)

            request.session['start_time'] = timestart.strftime("%Y%m%d%H%M%S")
            request.session['end_time'] = timeend.strftime("%Y%m%d%H%M%S")

    context['startd'] = timestart.strftime("%Y-%m-%d")
    context['startt'] = timestart.strftime("%H:%M")
    context['endd'] = timeend.strftime("%Y-%m-%d")
    context['endt'] = timeend.strftime("%H:%M")

    timestart = timestart.strftime("%Y%m%d%H%M%S")
    timeend = timeend.strftime("%Y%m%d%H%M%S")
    
    query = ref.order_by_key().start_at(timestart).end_at(timeend)
    sensor_data = query.get()
    sensor_data = [sensor_data[k] for k in sensor_data.keys()]

    if current_var == "loc":
        df = pd.DataFrame(sensor_data)
        fig = px.scatter_geo(df, lat='lat', lon='lng', hover_name='tiempo', title='Sensor Map', projection='natural earth')

    else:
        tiempo = [datetime.strptime(entry['fecha'] + entry['tiempo'], "%d/%m/%Y%H:%M:%S") for entry in sensor_data]
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

