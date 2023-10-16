# Semi-autonomus Environmental Station
Project for Engineering Projects' (O-2023) course at Universidad Iberoamericana CDMX

## Description
In this project we develop a semi-autonomous environmental station for easy data gathering and a website to sync data from the device and share with the world.

## How to run
Create a python virtual environment (not strictly necesary but highly recommended), then install the requirements into your new virtual evnvironment and run
the service. It will default to port 8000.
~~~
python -m venv .venv # Crea un entorno virtual en el folder ".venv"
# Activa el entorno virtual
./.venv/Scripts/Activate.ps1 # Windows Powershell
# ./.venv/Scripts/activate.bat # Windows cmd
# source .venv/bin/activate # Unix
python -m pip install -r requirements.txt # Instala las dependencias del proyecto en el entorno virtual
python manage.py runserver # Abre el sitio en http//localhost:8000
~~~