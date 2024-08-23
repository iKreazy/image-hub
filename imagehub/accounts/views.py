from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import LoginUserForm, RegisterUserForm, SettingsUserForm


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'accounts/signin.html'
    extra_context = {'title': 'Sign In'}

    def get_success_url(self):
        return reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


class UserLogout(LogoutView):
    def get_success_url(self):
        return reverse_lazy('index')


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'accounts/signup.html'
    extra_context = {'title': 'Sign Up'}
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object, backend='django.contrib.auth.backends.ModelBackend')
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)


class UserSettings(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = SettingsUserForm
    template_name = 'accounts/settings.html'
    extra_context = {'title': 'Settings'}
    login_url = reverse_lazy('signin')

    def get_success_url(self):
        return reverse_lazy('settings')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)

        if 'delete_avatar' in self.request.POST:
            if user.avatar:
                user.avatar.delete(save=False)
                user.avatar = None
        else:
            if form.cleaned_data['avatar']:
                if user.avatar:
                    user.avatar.delete(save=False)
                user.avatar = form.cleaned_data['avatar']

        current_password = form.cleaned_data.get('current_password')
        if current_password and user.check_password(current_password):
            user.set_password(form.cleaned_data['password1'])
            update_session_auth_hash(self.request, user)

        user.save()
        return super().form_valid(form)
