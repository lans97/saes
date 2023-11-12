from django import forms

class LoginForm(forms.Form):
    user_email = forms.CharField(label="Email", max_length=100)
