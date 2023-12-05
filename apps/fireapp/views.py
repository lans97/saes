from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Sensor
from .forms import SignUpForm, SensorForm

import plotly.express as px
from django.http import HttpResponse, JsonResponse
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
    ref = db.reference("/sensors")
    currentUser = request.user
    saes_log=""
    saes_err=""

    if request.method == 'POST':
        form = SensorForm(request.POST)
        if form.is_valid():
            sensor = form.save(commit=False)

            sensor_online = ref.get(str(sensor.sensor_id))
            if ref.get(str(sensor.sensor_id)) is None:
                saes_err = "Sensor ID not found"
            else:
                if sensor_online.get('user') != currentUser:
                    saes_err = "Sensor User does not match"
                else:
                    sensor.user = request.user
                    sensor.save()
                    saes_log="Sensor added to your dashboard"

            return redirect('sensors')
    else:
        form = SensorForm()
    
    #request.session.set
    return render(request, 'fireapp/add-sensor.html', { 'form': form })

@login_required
def dashboard_view(request, sensor_id):
    ref = db.reference("/sensors/" + sensor_id + "/data")
    context = {}
    context['sensor_id'] = sensor_id

    options = {"Humedad": 'hum', "Intensidad Luminosa": 'luz', "Sonido": 'sonido', "Temperatura": 'temp'}
    units = {"Humedad": '[]', "Intensidad Luminosa": '[]', "Sonido": '[dB]', "Temperatura": '[°C]'}

    curr_var_list = request.session.get('plot_vars', ["Temperatura"])
    
    request.session['curr_sensor'] = sensor_id
    request.session.save()

    timestart_str = request.session.get('start_time', datetime.now().strftime("%Y%m%d%H%M%S"))
    timeend_str = request.session.get('end_time', datetime.now().strftime("%Y%m%d%H%M%S"))

    timestart = datetime.strptime(timestart_str, "%Y%m%d%H%M%S")
    timeend = datetime.strptime(timeend_str, "%Y%m%d%H%M%S")
    current_var = ""
    
    if request.method == 'POST':
        curr_var_list = request.POST.getlist('plot-var', ["Temperatura"])
        request.session['plot_vars'] = curr_var_list
        request.session.save()
        if 'map' in request.POST:
            current_var = 'loc'
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
    if sensor_data != []:
        if current_var == "loc":
            df = pd.DataFrame(sensor_data)
            fig = px.scatter_geo(df, lat='lat', lon='lng', hover_name='altura', title='Sensor Map', projection='natural earth')

        else:
            tiempo = [datetime.strptime(entry['fecha'] + entry['tiempo'], "%d/%m/%Y%H:%M:%S") for entry in sensor_data]
            df = pd.DataFrame(sensor_data)
            df = df.drop(['altura', 'lat', 'lng', 'fecha', 'tiempo'], axis=1)
            df.rename(columns={v: k+" "+units[k] for k, v in options.items()}, inplace=True)
            df.insert(0, "Tiempo", tiempo)

            # Plotly
            fig = px.scatter(df, x='Tiempo', y=[var+" "+units[var] for var in curr_var_list], title=sensor_id)
        plot_json = fig.to_json()
        context['plot_json'] = plot_json
        context['sensor_status'] = "True"
    else:
        context['sensor_status'] = "False"

    context['vars_list'] = list(options.keys())
    context['sel_vars'] = curr_var_list

    return render(request, 'fireapp/dashboard.html', context)

def logout_view(request):
    logout(request)
    next_url = request.POST.get('next') or request.GET.get('next') or 'landing-home'
    return redirect(next_url)

def download_csv(request):
    sensor_id = request.session.get('curr_sensor')
    ref = db.reference("/sensors/" + sensor_id + "/data")
    options = {"Humedad": 'hum', "Intensidad Luminosa": 'luz', "Sonido": 'sonido', "Temperatura": 'temp'}
    units = {"Humedad": '[]', "Intensidad Luminosa": '[]', "Sonido": '[dB]', "Temperatura": '[°C]'}
    curr_var_list = request.session.get('plot_vars', list(options.keys()))
    
    timestart_str = request.session.get('start_time', datetime.now().strftime("%Y%m%d%H%M%S"))
    timeend_str = request.session.get('end_time', datetime.now().strftime("%Y%m%d%H%M%S"))

    timestart = datetime.strptime(timestart_str, "%Y%m%d%H%M%S")
    timeend = datetime.strptime(timeend_str, "%Y%m%d%H%M%S")

    timestart = timestart.strftime("%Y%m%d%H%M%S")
    timeend = timeend.strftime("%Y%m%d%H%M%S")
    
    query = ref.order_by_key().start_at(timestart).end_at(timeend)
    sensor_data = query.get()
    sensor_data = [sensor_data[k] for k in sensor_data.keys()]
    
    tiempo = [datetime.strptime(entry['fecha'] + entry['tiempo'], "%d/%m/%Y%H:%M:%S") for entry in sensor_data]
    df = pd.DataFrame(sensor_data)
    df = df.drop(['altura', 'lat', 'lng', 'fecha', 'tiempo'], axis=1)
    df.rename(columns={v: k+" "+units[k] for k, v in options.items()}, inplace=True)
    df.insert(0, "Tiempo", tiempo)

    if sensor_data != []:
        for k, v in options.items():
            if k not in curr_var_list:
                df = df.drop(columns=[k+" "+units[k]], axis=1)
    else:
        return HttpResponse("Data not found", status=404)

    csv_data = df.to_csv(index=False)
    response = HttpResponse(csv_data, content_type='text/csv')
    return response