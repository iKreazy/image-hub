from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label='Username or E-mail',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'justin.walter@email.com', 'autofocus': True})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(
        label='First name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Justin', 'autofocus': True}),
        required=True
    )
    email = forms.EmailField(
        label='Email address',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'justin.walter@email.com'}),
        required=True
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Re-enter password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2']
        labels = {
            'last_name': 'Last name',
            'username': 'Username'
        }
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Walter'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'justinwalter'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.pop('autofocus', None)
        if 'usable_password' in self.fields:
            del self.fields['usable_password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email
