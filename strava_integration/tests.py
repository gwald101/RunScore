from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class StravaIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(phone_number='+15555555555', password='testpassword')
        self.client.force_login(self.user)
        self.connect_url = reverse('strava:connect')
        self.callback_url = reverse('strava:callback')

    def test_connect_redirect(self):
        response = self.client.get(self.connect_url)
        # Should redirect to callback with fake code because of placeholder creds
        self.assertRedirects(response, 'http://localhost:8000/strava/callback/?code=fake_auth_code', fetch_redirect_response=False)

    def test_callback_success(self):
        response = self.client.get(self.callback_url, {'code': 'fake_auth_code'})
        self.assertRedirects(response, reverse('dashboard:index'))
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.strava_refresh_token, 'fake_refresh_token')
