from django.db import models
from django.conf import settings

class MileageLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mileage_logs')
    week_start_date = models.DateField()
    total_mileage = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-week_start_date']
        unique_together = ('user', 'week_start_date')

    def __str__(self):
        return f"{self.user.phone_number} - {self.week_start_date}: {self.total_mileage} miles"
