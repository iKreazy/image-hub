from django.contrib.auth import login, get_user_model, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy

from .forms import LoginUserForm, RegisterUserForm, SettingsUserForm, RecoveryForm, RecoveryConfirmForm


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


class RecoveryView(PasswordResetView):
    form_class = RecoveryForm
    template_name = 'accounts/recovery.html'
    email_template_name = 'accounts/recovery_email.html'
    extra_context = {'title': 'Recovery', 'template_name': 'accounts/recovery_form.html'}
    success_url = reverse_lazy('recovery_done')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        if not get_user_model().objects.filter(email=email).exists():
            form.add_error('email', 'The user with the specified email is not registered')
            return self.form_invalid(form)

        response = super().form_valid(form)
        self.request.session['recovery_in_progress'] = True
        return response


class RecoveryDoneView(PasswordResetDoneView):
    template_name = 'accounts/recovery.html'
    extra_context = {'title': 'Recovery', 'template_name': 'accounts/recovery_done.html'}

    def dispatch(self, *args, **kwargs):
        if not self.request.session.get('recovery_in_progress'):
            return redirect('recovery')
        return super().dispatch(*args, **kwargs)


class RecoveryConfirmView(PasswordResetConfirmView):
    form_class = RecoveryConfirmForm
    template_name = 'accounts/recovery.html'
    extra_context = {'title': 'Recovery', 'template_name': 'accounts/recovery_confirm.html'}
    success_url = reverse_lazy('recovery_complete')

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'recovery_in_progress' in self.request.session:
            del self.request.session['recovery_in_progress']
        return response


class RecoveryCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/recovery.html'
    extra_context = {'title': 'Recovery', 'template_name': 'accounts/recovery_complete.html'}


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
