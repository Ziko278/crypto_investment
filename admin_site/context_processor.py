from django.db.models import F

from admin_site.models import SiteInfoModel, SiteSettingModel
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from communication.models import UserNotificationModel


def general_info(request):
    user_notification = None
    if request.user.is_authenticated:
        user_notification = UserNotificationModel.objects.filter(user=request.user, is_read=False).count()

    return {
        'site_info': SiteInfoModel.objects.first(),
        'site_setting': SiteSettingModel.objects.first(),
        'user_notification_count': user_notification
    }
