from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or E-mail',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'justin.walter@email.com',
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
        })
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']
