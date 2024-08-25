import os

from PIL import Image
from io import BytesIO

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from django.conf import settings


class UserSettingsTest(TestCase):
    def setUp(self):
        self.model = get_user_model()
        self.data_auth = {
            'first_name': 'Name',
            'last_name': 'Surname',
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'testpassword'
        }
        self.user = self.model.objects.create_user(**self.data_auth)
        self.url = reverse('settings')

        self.old_user = {'username': 'olduser', 'email': 'olduser@email.com', 'password': 'testpassword'}
        self.model.objects.create_user(**self.old_user)

        self.user_auth = self.client.login(**self.data_auth)

    @staticmethod
    def generate_test_avatar():
        img = Image.new("RGB", (100, 100), (0, 255, 0))
        img_file = BytesIO()
        img.save(img_file, 'jpeg')
        img_file.seek(0)
        return SimpleUploadedFile('test_avatar.jpg', img_file.read(), content_type='image/jpeg')

    def test_settings_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/settings.html')

    def test_settings_not_auth(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('signin') + '?next=' + self.url)

    def test_change_first_name(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['first_name'] = 'NewFirstName'

        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data_auth['first_name'])

    def test_change_last_name(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['last_name'] = 'NewLastName'

        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_name, data_auth['last_name'])

    def test_change_email_to_existing(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['email'] = self.old_user['email']

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_email(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['email'] = 'newtest@email.com'

        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data_auth['email'])

    def test_change_username_to_existing(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['username'] = self.old_user['username']

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_username_wrong_format(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['username'] = 'invalid-username!'

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_username(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['username'] = 'new_username'

        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data_auth['username'])

    def test_change_password_without_current_password(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['password1'] = 'newpassword@1'
        data_auth['password2'] = 'newpassword@1'

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_password_with_incorrect_current_password(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['current_password'] = 'wrongpassword'
        data_auth['password1'] = 'newpassword@1'
        data_auth['password2'] = 'newpassword@1'

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_password_not_match(self):
        data_auth = self.data_auth
        data_auth['current_password'] = data_auth.pop('password')
        data_auth['password1'] = 'newpassword@1'
        data_auth['password2'] = 'wrongpassword'

        response = self.client.post(self.url, data_auth)
        self.assertTrue(bool(response.context['form'].errors), "The form must contain errors")

    def test_change_password(self):
        data_auth = self.data_auth
        data_auth['current_password'] = data_auth.pop('password')
        data_auth['password1'] = 'newpassword@1'
        data_auth['password2'] = 'newpassword@1'

        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data_auth['password1']))

    def test_avatar_upload_and_update(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['avatar'] = self.generate_test_avatar()
        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.avatar), "Missing path value avatar")

        avatar_path = os.path.join(settings.MEDIA_ROOT, os.path.normpath(self.user.avatar.name))
        self.assertTrue(os.path.isfile(avatar_path),
                        "The uploaded avatar image is missing from the project media folder")

        if os.path.isfile(avatar_path):
            os.remove(avatar_path)

    def test_avatar_old_delete(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['avatar'] = self.generate_test_avatar()
        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.avatar), "Missing path value avatar")

        old_avatar_path = os.path.join(settings.MEDIA_ROOT, os.path.normpath(self.user.avatar.name))
        self.assertTrue(os.path.isfile(old_avatar_path),
                        "The uploaded avatar image is missing from the project media folder")

        data_auth['avatar'] = self.generate_test_avatar()
        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.avatar), "Missing path value avatar")

        new_avatar_path = os.path.join(settings.MEDIA_ROOT, os.path.normpath(self.user.avatar.name))
        self.assertTrue(os.path.isfile(new_avatar_path),
                        "The uploaded avatar image is missing from the project media folder")

        if os.path.isfile(new_avatar_path):
            os.remove(new_avatar_path)

        self.assertFalse(os.path.isfile(old_avatar_path),
                         "The old avatar photo was not removed from the media directory")

    def test_avatar_delete(self):
        data_auth = self.data_auth
        data_auth.pop('password')
        data_auth['avatar'] = self.generate_test_avatar()
        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertTrue(bool(self.user.avatar), "Missing path value avatar")

        avatar_path = os.path.join(settings.MEDIA_ROOT, os.path.normpath(self.user.avatar.name))
        self.assertTrue(os.path.isfile(avatar_path),
                        "The uploaded avatar image is missing from the project media folder")

        data_auth.pop('avatar')
        data_auth['delete_avatar'] = True
        self.client.post(self.url, data_auth)
        self.user.refresh_from_db()
        self.assertFalse(bool(self.user.avatar), "The avatar path value should be empty")

        self.assertFalse(os.path.isfile(avatar_path),
                         "The avatar photo has not been removed from the media directory")
