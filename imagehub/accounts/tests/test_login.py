from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model


class LoginUserTest(TestCase):
    def setUp(self):
        self.model = get_user_model()
        self.user = {'username': 'testuser', 'password': 'testpassword'}
        self.model.objects.create_user(**self.user, email='test@email.com')
        self.url = reverse('signin')

    def test_login_user_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signin.html')

    def test_login_user_is_auth(self):
        self.client.login(**self.user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse_lazy('index'))

        user = self.model.objects.get(username=self.user['username'])
        self.assertTrue(user.is_authenticated, "The user must be authorized")

    def test_login_using_email_is_auth(self):
        self.client.logout()

        self.client.login(username='test@email.com', password=self.user['password'])

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse_lazy('index'))

        user = self.model.objects.get(username=self.user['username'])
        self.assertTrue(user.is_authenticated, "The user must be authorized")

    def test_login_using_email_wrong_password(self):
        self.client.logout()

        data_auth = {'username': 'test@email.com', 'password': 'wrongpassword'}
        is_auth = self.client.login(**data_auth)
        self.assertFalse(is_auth, "The user must not be logged in")

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_login_using_wrong_email_is_auth(self):
        self.client.logout()

        is_auth = self.client.login(username='test@wrong_email.com', password=self.user['password'])
        self.assertFalse(is_auth, "The user must not be logged in")

    def test_login_post_success(self):
        self.client.logout()

        response = self.client.post(self.url, self.user)
        self.assertRedirects(response, reverse_lazy('index'))

        user = self.model.objects.get(username=self.user['username'])
        self.assertTrue(user.is_authenticated, "The user must be authorized")

    def test_login_post_invalid(self):
        self.client.logout()

        response = self.client.post(self.url, {'username': 'wronguser', 'password': self.user['password']})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

