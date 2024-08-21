from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .forms import LoginUserForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'accounts/signin.html'
    extra_context = {'title': 'Sign In'}

    def get_success_url(self):
        return reverse_lazy('index')


class UserLogout(LogoutView):
    def get_success_url(self):
        return reverse_lazy('index')
