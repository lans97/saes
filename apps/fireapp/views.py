from django.shortcuts import render

from django.conf import settings
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'secrets/key.json'))

firebase_admin.initialize_app(cred, {
    'databaseURL': "https://saes-dde36-default-rtdb.firebaseio.com/"
})

ref = db.reference('Data')

# Create your views here.

def index(request):
    name = ref.child('Name').get()
    stack = ref.child('Stack').get()
    framework = ref.child('Framework').get()

    context = {
        'name':name,
        'stack':stack,
        'framework':framework
        }
    return render(request, 'fireapp/index.html', context)
