from django.contrib.auth.models import User
from django.db import models
from admin_site.models import CurrencyModel


class TradingPlanModel(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    pairs = models.IntegerField()
    leverage = models.IntegerField()
    pip = models.FloatField()
    has_swap_fee = models.BooleanField()
    STATUS = (('active', 'ACTIVE'), ('inactive', 'INACTIVE'))
    status = models.CharField(max_length=30, blank=True, default='active', choices=STATUS)

    def __str__(self):
        return self.name.title()


class SignalPlanModel(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    strength = models.IntegerField()
    STATUS = (('active', 'ACTIVE'), ('inactive', 'INACTIVE'))
    status = models.CharField(max_length=30, blank=True, default='active', choices=STATUS)

    def __str__(self):
        return self.name.title()


class MiningPlanModel(models.Model):
    name = models.CharField(max_length=100)
    amount = models.FloatField()
    asset = models.CharField(max_length=100)
    duration = models.IntegerField()
    STATUS = (('active', 'ACTIVE'), ('inactive', 'INACTIVE'))
    status = models.CharField(max_length=30, blank=True, default='active', choices=STATUS)

    def __str__(self):
        return self.name.title()




