from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.dashboard_url = reverse('dashboard:index')
        self.user_data = {
            'phone_number': '+15555555555',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }

    def test_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertRedirects(response, self.dashboard_url)
        self.assertTrue(User.objects.filter(phone_number=self.user_data['phone_number']).exists())

    def test_login(self):
        User.objects.create_user(phone_number=self.user_data['phone_number'], password=self.user_data['password'])
        response = self.client.post(self.login_url, {
            'username': self.user_data['phone_number'], # AuthenticationForm uses 'username' field
            'password': self.user_data['password']
        })
        self.assertRedirects(response, self.dashboard_url)
        
    def test_dashboard_requires_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.dashboard_url}')
