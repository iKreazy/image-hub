from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.management import BaseCommand, CommandError
from django.apps import apps

import os
import random
import requests
from faker import Faker
from requests import HTTPError

from main.models import CommandExecution


class Command(BaseCommand):
    help = 'Generate test data including profiles, categories, and images'

    def add_arguments(self, parser):
        parser.add_argument('superuser', type=str, help='Username of the admin user')
        parser.add_argument('password', type=str, help='Password of the admin user')

    def handle(self, *args, **options):
        if CommandExecution.objects.filter(command_name='imagetest').exists():
            self.stdout.write(self.style.ERROR('This command has already been executed and cannot be run again.'))
            return

        def is_runserver():
            try:
                return requests.get(f'{settings.SITE_URL}').status_code == 200
            except requests.RequestException:
                return False

        if not is_runserver():
            self.stdout.write(self.style.ERROR('Server is not running. Please start the server and try again.'))
            return

        admin = authenticate(username=options['superuser'], password=options['password'])
        if admin is None:
            raise CommandError('Invalid superuser or password.')

        if not admin.is_superuser:
            raise CommandError('The provided user is not a superuser.')

        def get_url(name, *args, **kwargs):
            return f"{settings.SITE_URL}{reverse(name, args=args, kwargs=kwargs)}"

        def get_token(username, password):
            response = requests.post(get_url('api-token'), json={'username': username, 'password': password})
            if response.status_code == 200:
                return response.json()['access']
            raise HTTPError(f'Failed to get token: {response.status_code} {response.text}')

        def create_category(token, name, slug):
            response = requests.post(
                get_url('api-category-create'),
                json={'name': name, 'slug': slug},
                headers={'Authorization': f'Bearer {token}'})
            if response.status_code == 201:
                return response.json()['id']
            raise HTTPError(f'Failed to create category: {response.status_code} {response.text}')

        def create_account(username, password, email, first_name, last_name):
            response = requests.post(get_url('api-account-signup'), json={
                'username': username,
                'password': password,
                'password2': password,
                'email': email,
                'first_name': first_name,
                'last_name': last_name
            })
            if response.status_code == 201:
                return response.json()['id']
            else:
                raise HTTPError(f'Failed to create account: {response.status_code} {response.text}')

        def upload_avatar(token, file_path):
            with open(file_path, 'rb') as file:
                response = requests.patch(
                    get_url('api-account-settings'),
                    files={'avatar': file},
                    headers={'Authorization': f'Bearer {token}'}
                )
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPError(f'Failed to upload avatar: {response.status_code} {response.text}')

        def upload_image(token, file_path, description, category_id):
            with open(file_path, 'rb') as file:
                response = requests.post(
                    get_url('api-image-upload'),
                    files={'file': file},
                    data={
                        'description': description,
                        'category_id': category_id
                    },
                    headers={'Authorization': f'Bearer {token}'}
                )
            if response.status_code == 201:
                return response.json()['id']
            else:
                raise HTTPError(f'Failed to upload image: {response.status_code} {response.text}')

        gen_data = Faker()
        categories = {
            'cars': 'Cars',
            'girls': 'Girls',
            'animals': 'Animals',
            'other': 'Others'
        }
        base_path = apps.get_app_config('api').path
        image_path = os.path.join(base_path, 'imagetest_data')

        # Create categories
        admin_token = get_token(options['superuser'], options['password'])
        category_ids = dict()
        for slug, name in categories.items():
            category_id = create_category(admin_token, name, slug)
            category_ids[slug] = category_id
            print(f'Category "{name}" created with ID: {category_id}')

        # Create accounts
        accounts = list()
        for _ in range(5):
            user = dict(
                username=gen_data.user_name(),
                password=gen_data.password(length=12),
                email=gen_data.email(domain='gmail.com'),
                first_name=gen_data.first_name(),
                last_name=gen_data.last_name()
            )

            account_id = create_account(**user)
            accounts.append({
                'token': get_token(user['username'], user['password']),
                'username': user['username'],
                'password': user['password'],
                'user_id': account_id
            })
            print(f'Account "{user["username"]}" created with ID: {account_id}')

        # Update avatars
        used_avatars = set()
        avatar_path = os.path.join(image_path, 'avatars')
        avatar_files = os.listdir(avatar_path)
        for account in accounts:
            while True:
                random_avatar = random.choice(avatar_files)
                if random_avatar not in used_avatars:
                    used_avatars.add(random_avatar)
                    break

            user_token = get_token(account['username'], account['password'])
            upload_avatar(user_token, os.path.join(avatar_path, random_avatar))
            print(f'Avatar "{random_avatar}" uploaded for account "{account["username"]}"')

        # Upload images
        for category in ['cars', 'girls', 'animals', 'other']:
            folder_path = os.path.join(image_path, category)
            image_files = sorted(os.listdir(folder_path))

            for image_file in image_files:
                file_path = os.path.join(folder_path, image_file)
                description = gen_data.text(max_nb_chars=random.randint(128, 1024)) if random.randint(0, 1) else ''
                account = random.choice(accounts)

                upload_image(account['token'], file_path, description, category_ids[category])
                print(f'Image "{image_file}" from category "{category}" uploaded by account "{account["username"]}"')

        CommandExecution.objects.create(command_name='imagetest')
        self.stdout.write(self.style.SUCCESS('Test data for accounts and categories generated, images uploaded successfully!'))
