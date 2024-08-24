from django.contrib.auth.models import User
from django.db import models
from admin_site.models import CurrencyModel


class UserNotificationModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='user_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.__str__()