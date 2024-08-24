import barcode
from django.db import models

from barcode.writer import ImageWriter


def generate_barcode(address):
    code = barcode.Code39(address, writer=ImageWriter(), add_checksum=False)
    file_name = f'{address}'
    file_path = f'media/barcode/address/{file_name}'
    code.save(file_path)
    #
    return file_path + '.png'


class SiteInfoModel(models.Model):
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=50)
    mobile_1 = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    address = models.CharField(max_length=255, null=True, blank=True)

    logo = models.FileField(upload_to='images/setting/logo')

    # social media handles
    facebook_handle = models.CharField(max_length=100, null=True, blank=True)
    instagram_handle = models.CharField(max_length=100, null=True, blank=True)
    twitter_handle = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.short_name.upper()


class CurrencyModel(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    symbol = models.CharField(max_length=10)
    STATUS = (
        ('active', 'ACTIVE'), ('inactive', 'INACTIVE')
    )
    status = models.CharField(max_length=10, choices=STATUS, blank=True, default='active')

    def __str__(self):
        return self.code.upper()


class SupportedCryptoModel(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    address = models.CharField(max_length=250)
    old_address = models.CharField(max_length=250, null=True, blank=True)
    barcode = models.FileField(upload_to='barcode/address', null=True, blank=True)
    STATUS = (
        ('active', 'ACTIVE'), ('inactive', 'INACTIVE')
    )
    status = models.CharField(max_length=10, choices=STATUS, blank=True, default='active')

    def __str__(self):
        return self.code.upper()

    def save(self, *args, **kwargs):
        if self.address != self.old_address:
            barcode_file_path = generate_barcode(self.address)
            self.old_address = self.address
            self.barcode = barcode_file_path

        super(SupportedCryptoModel, self).save(*args, **kwargs)


class SiteSettingModel(models.Model):
    email_confirmation = models.BooleanField(default=False)
    minimum_deposit = models.FloatField(default=50)
    referral_bonus = models.FloatField(default=10, blank=True)
    referral_payment_before_bonus = models.BooleanField(default=True, blank=False)
    swap_fee = models.FloatField(default=0.05)
    default_currency = models.ForeignKey(CurrencyModel, on_delete=models.RESTRICT)
    WALLET_TYPE = (('holding', 'HOLDING BALANCE'), ('trading', 'TRADING BALANCE'))
    default_funding_account = models.CharField(max_length=30, choices=WALLET_TYPE)

    def __str__(self):
        return 'SITE SETTING'


class AssetModel(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=50)
    category = models.CharField(max_length=50, default='crypto')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name.title()