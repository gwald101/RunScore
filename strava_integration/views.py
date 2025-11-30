from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .services import StravaService

@login_required
def connect(request):
    service = StravaService()
    auth_url = service.get_authorization_url()
    return redirect(auth_url)

@login_required
def callback(request):
    code = request.GET.get('code')
    if code:
        service = StravaService()
        tokens = service.exchange_token(code)
        
        # Save tokens to user profile
        request.user.strava_refresh_token = tokens.get('refresh_token')
        request.user.save()
        
        # Trigger initial data fetch (mocked for now)
        service.fetch_initial_data(request.user)
        
        return redirect('dashboard:index')
    return redirect('dashboard:index')
