from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os

@login_required
def index(request):
    from django.utils import timezone
    from datetime import timedelta
    from strava_integration.models import MileageLog
    
    user = request.user
    today = timezone.now().date()
    current_week_start = today - timedelta(days=today.weekday())
    
    # Acute Mileage (Current Week)
    acute_log = MileageLog.objects.filter(user=user, week_start_date=current_week_start).first()
    acute_mileage = acute_log.total_mileage if acute_log else 0.0
    
    # Chronic Mileage (Avg of last 4 weeks)
    last_4_weeks_start = current_week_start - timedelta(weeks=4)
    chronic_logs = MileageLog.objects.filter(
        user=user, 
        week_start_date__lt=current_week_start,
        week_start_date__gte=last_4_weeks_start
    )
    
    total_chronic_mileage = sum(log.total_mileage for log in chronic_logs)
    chronic_mileage = total_chronic_mileage / 4.0
    
    # Critical Score
    if chronic_mileage > 0:
        critical_score = acute_mileage / chronic_mileage
    else:
        critical_score = 0.0
        
    # Recommended Capacity (Next Week)
    recommended_capacity = chronic_mileage * 1.25
    
    # Firebase config for templates
    firebase_config = {
        'api_key': os.getenv('FIREBASE_API_KEY'),
        'auth_domain': os.getenv('FIREBASE_AUTH_DOMAIN'),
        'project_id': os.getenv('FIREBASE_PROJECT_ID'),
        'storage_bucket': os.getenv('FIREBASE_STORAGE_BUCKET'),
        'messaging_sender_id': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
        'app_id': os.getenv('FIREBASE_APP_ID'),
    }
    
    context = {
        'acute_mileage': round(acute_mileage, 1),
        'chronic_mileage': round(chronic_mileage, 1),
        'critical_score': round(critical_score, 2),
        'recommended_capacity': round(recommended_capacity, 1),
        'firebase_config': firebase_config,
    }
    
    return render(request, 'dashboard/index.html', context)
