from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, Select, TextInput, RadioSelect, CheckboxInput, CheckboxSelectMultiple, DateInput
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError
from investment.models import *


class TradingPlanForm(ModelForm):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['has_swap_fee']:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control',
                    'autocomplete': 'off'
                })

    class Meta:
        model = TradingPlanModel
        fields = '__all__'

        widgets = {

        }


class SignalPlanForm(ModelForm):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = SignalPlanModel
        fields = '__all__'

        widgets = {

        }


class MiningPlanForm(ModelForm):
    """"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'autocomplete': 'off'
            })

    class Meta:
        model = MiningPlanModel
        fields = '__all__'

        widgets = {

        }