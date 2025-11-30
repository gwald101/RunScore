from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
    # Ensure we divide by 4 even if some weeks are missing (treat missing as 0)
    chronic_mileage = total_chronic_mileage / 4.0
    
    # Critical Score
    if chronic_mileage > 0:
        critical_score = acute_mileage / chronic_mileage
    else:
        critical_score = 0.0 # Or handle as "Not enough data"
        
    # Recommended Capacity (Next Week)
    recommended_capacity = chronic_mileage * 1.25
    
    context = {
        'acute_mileage': round(acute_mileage, 1),
        'chronic_mileage': round(chronic_mileage, 1),
        'critical_score': round(critical_score, 2),
        'recommended_capacity': round(recommended_capacity, 1),
    }
    
    return render(request, 'dashboard/index.html', context)
