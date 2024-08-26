from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model


class UserLogoutTest(TestCase):
    def setUp(self):
        self.model = get_user_model()
        self.user = {'username': 'testuser', 'password': 'testpassword'}
        self.model.objects.create_user(**self.user)
        self.url = reverse('logout')

    def test_user_logout(self):
        is_auth = self.client.login(**self.user)
        self.assertTrue(is_auth, "The user must be authorized")

        response = self.client.post(self.url)
        self.assertRedirects(response, reverse_lazy('index'))
        self.assertNotIn('_auth_user_id', self.client.session, "The user must not be logged in")
