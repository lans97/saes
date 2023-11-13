from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Sensor

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['sensor_id', 'name', 'description' ]
