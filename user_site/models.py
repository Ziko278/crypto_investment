from django.contrib.auth.models import User
from django.db import models
from admin_site.models import CurrencyModel, SupportedCryptoModel, AssetModel
from investment.models import TradingPlanModel


class UserProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, related_name='user_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.EmailField()
    phone_number = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    currency = models.ForeignKey(CurrencyModel, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='user/profile_photo', blank=True, null=True)
    referrals = models.ManyToManyField('self', blank=True)
    email_verified = models.BooleanField(default=False, blank=True)
    identity_verified = models.BooleanField(default=False, blank=True)
    identity_verification_pending = models.BooleanField(default=False, blank=True)
    identity_document_1 = models.FileField(upload_to='profile/verification', blank=True, null=True)
    identity_document_2 = models.FileField(upload_to='profile/verification', blank=True, null=True)
    address_verified = models.BooleanField(default=False, blank=True)
    address_verification_pending = models.BooleanField(default=False, blank=True)
    address_document = models.FileField(upload_to='profile/verification', blank=True, null=True)
    last_verification_code = models.CharField(max_length=10, null=True, blank=True)
    has_deposited = models.BooleanField(default=False, blank=False)
    trade_plan = models.OneToOneField(TradingPlanModel, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.first_name.title() + ' ' + self.last_name.title()


class UserWalletModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, related_name='user_wallet')
    holding_balance = models.FloatField(default=0.0)
    trading_balance = models.FloatField(default=0.0)
    mining_balance = models.FloatField(default=0.0)
    referral_balance = models.FloatField(default=0.0)

    def __str__(self):
        return self.user.username.title()


class UserAssetModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, related_name='user_asset')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    value = models.FloatField()

    def __str__(self):
        return self.name.title()


class UserFundingModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='funding_list')
    amount = models.FloatField()
    currency = models.ForeignKey(CurrencyModel, on_delete=models.SET_NULL, null=True, blank=True)
    WALLET_TYPE = (('holding', 'HOLDING BALANCE'), ('trading', 'TRADING BALANCE'))
    wallet_type = models.CharField(max_length=30, choices=WALLET_TYPE)
    payment_method = models.ForeignKey(SupportedCryptoModel, on_delete=models.SET_NULL, null=True, blank=True)
    payment_value = models.FloatField(null=True, blank=True)
    proof_of_payment = models.FileField(blank=True, null=True, upload_to='images/funding')
    status = models.CharField(max_length=30, blank=True, default='pending')  # pending, failed and completed
    previous_status = models.CharField(max_length=30, blank=True, null=True)  # pending, failed and completed
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.user.__str__()

    def save(self, *args, **kwargs):
        if self.status != self.previous_status:
            self.previous_status = self.status
            if self.status == 'completed':
                wallet = UserWalletModel.objects.get(user=self.user)
                if self.wallet_type == 'holding':
                    wallet.holding_balance += self.amount
                elif self.wallet_type == 'trading':
                    wallet.trading_balance += self.amount

                wallet.save()

        super(UserFundingModel, self).save(*args, **kwargs)


class UserWatchListModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, related_name='watch_lists')
    watch_lists = models.ManyToManyField(AssetModel, blank=True)


class AssetConversionModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    amount = models.FloatField(blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    name = models.CharField(max_length=30)
    symbol = models.CharField(max_length=30)
    direction = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return "{} - {} - {}".format(self.value, self.name, self.user.__str__())


class AssetValueModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    value = models.FloatField(default=0)
    name = models.CharField(max_length=30)
    symbol = models.CharField(max_length=30)

    def __str__(self):
        return "{} - {} - {}".format(self.value, self.name, self.user.__str__())


