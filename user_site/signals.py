from datetime import date
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from user_site.models import UserWalletModel, UserWatchListModel, AssetConversionModel, AssetValueModel
from admin_site.models import AssetModel
from datetime import datetime


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    user = instance
    if created:
        if not user.is_superuser:
            wallet = UserWalletModel.objects.create(user=user)
            wallet.save()

            user_watch_list = UserWatchListModel.objects.create(user=user)
            default_asset = AssetModel.objects.filter(is_default=True)
            asset_list = [asset.id for asset in default_asset]
            user_watch_list.watch_lists.add(*asset_list)


@receiver(post_save, sender=AssetConversionModel)
def buy_crypto(sender, instance, created, **kwargs):
    conversion = instance
    if created:
        try:
            asset_wallet = AssetValueModel.objects.get(user=conversion.user, name=conversion.name)
        except AssetValueModel.DoesNotExist:
            asset_wallet = AssetValueModel.objects.create(user=conversion.user, name=conversion.name, symbol=conversion.symbol)
            asset_wallet.save()
        if conversion.direction == 'crypto':
            asset_wallet.value += conversion.value
        elif conversion.direction == 'cash':
            asset_wallet.value -= conversion.value
        asset_wallet.save()
