import os
from django.conf import settings
import requests
from urllib.parse import urlencode

class StravaService:
    def __init__(self):
        self.client_id = os.getenv('STRAVA_CLIENT_ID')
        self.client_secret = os.getenv('STRAVA_CLIENT_SECRET')
        self.redirect_uri = 'http://localhost:8000/strava/callback/'

    def get_authorization_url(self):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': 'activity:read_all',
            'approval_prompt': 'force'
        }
        return f"https://www.strava.com/oauth/authorize?{urlencode(params)}"

    def exchange_token(self, code):
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()

    def fetch_initial_data(self, user):
        """Fetch real running data from Strava for the last 6 weeks."""
        print(f"Fetching real Strava data for user {user.phone_number}")
        
        from django.utils import timezone
        from datetime import timedelta
        from .models import MileageLog
        
        # Get access token
        if not user.strava_refresh_token:
            print("No refresh token available")
            return
            
        access_token = self._refresh_access_token(user.strava_refresh_token)
        
        # Calculate date range (6 weeks ago to now)
        today = timezone.now().date()
        six_weeks_ago = today - timedelta(weeks=6)
        
        # Fetch activities from Strava
        url = "https://www.strava.com/api/v3/athlete/activities"
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'after': int(six_weeks_ago.strftime('%s')),
            'per_page': 200
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        activities = response.json()
        
        # Process activities and aggregate by week
        weekly_mileage = {}
        current_week_start = today - timedelta(days=today.weekday())
        
        for activity in activities:
            # Only process running activities
            if activity.get('type') not in ['Run', 'VirtualRun']:
                continue
                
            # Parse activity date and determine week
            from datetime import datetime
            activity_date = datetime.fromisoformat(activity['start_date_local'].replace('Z', '+00:00')).date()
            week_start = activity_date - timedelta(days=activity_date.weekday())
            
            # Convert meters to miles
            distance_miles = activity['distance'] / 1609.34
            
            # Aggregate by week
            if week_start not in weekly_mileage:
                weekly_mileage[week_start] = 0.0
            weekly_mileage[week_start] += distance_miles
        
        # Save to database
        for week_start, mileage in weekly_mileage.items():
            MileageLog.objects.update_or_create(
                user=user,
                week_start_date=week_start,
                defaults={'total_mileage': round(mileage, 1)}
            )
            
        print(f"Saved {len(weekly_mileage)} weeks of data")
        
    def _refresh_access_token(self, refresh_token):
        """Get a new access token using the refresh token."""
        url = "https://www.strava.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        return response.json()['access_token']
