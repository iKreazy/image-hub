import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordResetForm, SetPasswordForm


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
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[A-Za-z0-9](?:[A-Za-z0-9_]*[A-Za-z0-9])?$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")

        if get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        return username


class RecoveryForm(PasswordResetForm):
    email = forms.EmailField(
        label='Email address',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'justin.walter@email.com'})
    )


class RecoveryConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    new_password2 = forms.CharField(
        label='Re-enter password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )


class SettingsUserForm(forms.ModelForm):
    first_name = forms.CharField(
        label='First name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Justin'})
    )
    email = forms.EmailField(
        label='Email address',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'justin.walter@email.com'})
    )
    avatar = forms.ImageField(
        label='Avatar',
        widget=forms.FileInput(attrs={'class': 'd-none', 'id': 'hidden-file-input'}),
        required=False
    )
    current_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        required=False
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        required=False
    )
    password2 = forms.CharField(
        label='Re-enter password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}),
        required=False
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'username', 'current_password', 'password1', 'password2']
        labels = {
            'last_name': 'Last name',
            'username': 'Username'
        }
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Walter'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'justinwalter'})
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        user = self.instance
        if user.email != email and get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[A-Za-z0-9](?:[A-Za-z0-9_]*[A-Za-z0-9])?$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")

        user = self.instance
        if user.username != username and get_user_model().objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get("current_password")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if current_password:
            if not self.instance.check_password(current_password):
                self.add_error('current_password', "Current password is incorrect.")
            else:
                if password1 and password1 != password2:
                    self.add_error('password2', "The two password fields didn't match.")
        else:
            if password1 or password2:
                self.add_error('current_password', "You must enter your current password to change the password.")
        return cleaned_data
