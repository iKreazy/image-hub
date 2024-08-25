from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model


class RegisterUserTest(TestCase):
    def setUp(self):
        self.model = get_user_model()

        self.old_user = {'username': 'olduser', 'email': 'olduser@email.com', 'password': 'testpassword'}
        self.model.objects.create_user(**self.old_user)

        self.user = {
            'first_name': 'Name',
            'username': 'testuser',
            'email': 'test@email.com',
            'password1': 'testpassword',
            'password2': 'testpassword'
        }
        self.url = reverse('signup')

    def test_register_user_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_register_user_empty_first_name(self):
        data_auth = self.user
        del data_auth['first_name']

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_empty_email(self):
        data_auth = self.user
        del data_auth['email']

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_password_not_match(self):
        data_auth = self.user
        data_auth['password2'] = 'wrongpassword'

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_wrong_username(self):
        data_auth = self.user
        data_auth['username'] = 'testuser_'

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_with_exist_username(self):
        data_auth = self.user
        data_auth['username'] = self.old_user['username']

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_with_exist_email(self):
        data_auth = self.user
        data_auth['email'] = self.old_user['email']

        response = self.client.post(self.url, data_auth)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_register_user_success(self):
        response = self.client.post(self.url, self.user)
        self.assertRedirects(response, reverse_lazy('index'))
        user_exists = self.model.objects.filter(username=self.user['username']).exists()
        self.assertTrue(user_exists, "The user is not registered")

        user = self.model.objects.get(username=self.user['username'])
        self.assertTrue(user.is_authenticated, "The user must be authorized")

    def test_register_user_is_auth(self):
        self.client.login(**self.old_user)

        response = self.client.get(self.url)
        self.assertRedirects(response, reverse_lazy('index'))
