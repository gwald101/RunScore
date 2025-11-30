from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from strava_integration.models import MileageLog

User = get_user_model()

class DashboardCalculationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(phone_number='+15555555555', password='testpassword')
        self.client.force_login(self.user)
        self.dashboard_url = reverse('dashboard:index')
        
        # Setup Dates
        self.today = timezone.now().date()
        self.current_week_start = self.today - timedelta(days=self.today.weekday())

    def test_score_calculation(self):
        # Create Acute Mileage (25 miles)
        MileageLog.objects.create(
            user=self.user,
            week_start_date=self.current_week_start,
            total_mileage=25.0
        )
        
        # Create Chronic Mileage (Avg 21 miles)
        # Weeks: 20, 22, 18, 24 -> Sum = 84 -> Avg = 21
        chronic_mileages = [20.0, 22.0, 18.0, 24.0]
        for i, mileage in enumerate(chronic_mileages):
            week_start = self.current_week_start - timedelta(weeks=i+1)
            MileageLog.objects.create(
                user=self.user,
                week_start_date=week_start,
                total_mileage=mileage
            )
            
        response = self.client.get(self.dashboard_url)
        
        # Expected Calculations:
        # Acute = 25.0
        # Chronic = 21.0
        # Score = 25 / 21 = 1.19
        # Capacity = 21 * 1.25 = 26.25
        
        self.assertEqual(response.context['acute_mileage'], 25.0)
        self.assertEqual(response.context['chronic_mileage'], 21.0)
        self.assertEqual(response.context['critical_score'], 1.19)
        self.assertEqual(response.context['recommended_capacity'], 26.2) # Rounded to 1 decimal place in view? View says round(x, 1)
        
    def test_no_data(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.context['acute_mileage'], 0.0)
        self.assertEqual(response.context['chronic_mileage'], 0.0)
        self.assertEqual(response.context['critical_score'], 0.0)
