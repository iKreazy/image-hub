from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class RecoveryUserTest(TestCase):
    def setUp(self):
        self.model = get_user_model()
        self.user_auth = {'username': 'testuser', 'email': 'test@email.com', 'password': 'testpassword'}
        self.user = self.model.objects.create_user(**self.user_auth)
        self.url = reverse('recovery')

    def test_recovery_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/recovery.html')
        self.assertEqual(response.context['template_name'], 'accounts/recovery_form.html')

    def test_recovery_post_user_not_match(self):
        response = self.client.post(self.url, {'email': 'test@wrongemail.com'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_recovery_done_not_in_progress(self):
        response = self.client.get(reverse('recovery_done'))
        self.assertRedirects(response, reverse('recovery'))

    def test_recovery_done_in_progress(self):
        response = self.client.post(self.url, {'email': self.user_auth['email']})
        self.assertRedirects(response, reverse('recovery_done'))
        self.assertIn('recovery_in_progress', self.client.session, "Session key recovery_in_progress missing")

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(uid + '/' + token, mail.outbox[0].body, "There is no password recovery link in the email")

    def test_recovery_confirm_view(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = reverse('recovery_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.post(url, follow=True)
        self.assertTemplateUsed(response, 'accounts/recovery.html')
        self.assertEqual(response.context['template_name'], 'accounts/recovery_confirm.html')

    def test_recovery_confirm_password_not_match(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = reverse('recovery_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.post(url, follow=True)

        url = response.redirect_chain[-1][0]
        new_password = {'new_password1': 'newpassword', 'new_password2': 'wrongpassword'}
        response = self.client.post(url, new_password)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_recovery_confirm(self):
        response = self.client.post(self.url, {'email': self.user_auth['email']})
        self.assertRedirects(response, reverse('recovery_done'))
        self.assertIn('recovery_in_progress', self.client.session, "Session key recovery_in_progress missing")

        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        url = reverse('recovery_confirm', kwargs={'uidb64': uid, 'token': token})
        response = self.client.post(url, follow=True)

        url = response.redirect_chain[-1][0]
        new_password = {'new_password1': 'newpassword@1', 'new_password2': 'newpassword@1'}
        response = self.client.post(url, new_password, follow=True)
        self.assertTemplateUsed(response, 'accounts/recovery.html')
        self.assertEqual(response.context['template_name'], 'accounts/recovery_complete.html')

        is_auth = self.client.login(username=self.user_auth['username'], password=new_password['new_password1'])
        self.assertTrue(is_auth, "The user must be authorized using the new password")
