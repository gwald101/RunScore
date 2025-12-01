from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import os

@login_required
def index(request):
    from django.utils import timezone
    from datetime import timedelta
    from strava_integration.models import MileageLog
    
    user = request.user
    
    # Determine "Current Week" based on Monday 3am rule
    # We subtract 3 hours from the current time. 
    # If it's Mon 2am, it becomes Sun 11pm -> Previous Week.
    # If it's Mon 4am, it becomes Mon 1am -> Current Week.
    now = timezone.now()
    adjusted_now = now - timedelta(hours=3)
    today = adjusted_now.date()
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
    
    # Calculate Date Range for Current Week
    week_end_date = current_week_start + timedelta(days=6)
    current_week_range = f"{current_week_start.strftime('%b %d')} - {week_end_date.strftime('%b %d')}"

    # Historical Data (Last 6 weeks: Current + 5 past)
    historical_data = []
    for i in range(6):
        # Calculate week start for this iteration (0 is current week, 1 is last week, etc.)
        week_start = current_week_start - timedelta(weeks=i)
        
        # Acute Mileage for this week
        log = MileageLog.objects.filter(user=user, week_start_date=week_start).first()
        acute = log.total_mileage if log else 0.0
        
        # Chronic Mileage (Avg of 4 weeks prior to this week)
        prior_4_weeks_start = week_start - timedelta(weeks=4)
        prior_logs = MileageLog.objects.filter(
            user=user,
            week_start_date__lt=week_start,
            week_start_date__gte=prior_4_weeks_start
        )
        total_prior = sum(l.total_mileage for l in prior_logs)
        chronic = total_prior / 4.0
        
        # ACWR
        ratio = acute / chronic if chronic > 0 else 0.0
        
        # Format Week Label
        if i == 0:
            week_label = "Current Week"
        else:
            week_end = week_start + timedelta(days=6)
            week_label = f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}"
            
        historical_data.append({
            'week_label': week_label,
            'acute': round(acute, 1),
            'chronic': round(chronic, 1),
            'acwr': round(ratio, 2) if chronic > 0 else "N/A"
        })
    
    context = {
        'acute_mileage': round(acute_mileage, 1),
        'chronic_mileage': round(chronic_mileage, 1),
        'critical_score': round(critical_score, 2),
        'recommended_capacity': round(recommended_capacity, 1),
        'current_week_range': current_week_range,
        'historical_data': historical_data,
        'firebase_config': firebase_config,
    }
    
    return render(request, 'dashboard/index.html', context)
