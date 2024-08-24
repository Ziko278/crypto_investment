from django.shortcuts import render, redirect
from django.urls import reverse
from django.core import serializers
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Q
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from investment.models import *
from investment.forms import *


class TradingPlanCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TradingPlanModel
    form_class = TradingPlanForm
    success_message = 'Trading Plan Added Successfully'
    template_name = 'investment/trading_plan/index.html'

    def get_success_url(self):
        return reverse('trading_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trading_plan'] = TradingPlanModel.objects.all().order_by('name')
        return context


class TradingPlanListView(LoginRequiredMixin, ListView):
    model = TradingPlanModel
    fields = '__all__'
    template_name = 'investment/trading_plan/index.html'
    context_object_name = "trading_plan_list"

    def get_queryset(self):
        return TradingPlanModel.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TradingPlanForm
        return context


class TradingPlanDetailView(LoginRequiredMixin, DetailView):
    model = TradingPlanModel
    fields = '__all__'
    template_name = 'investment/trading_plan/detail.html'
    context_object_name = "trading_plan"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class TradingPlanUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TradingPlanModel
    form_class = TradingPlanForm
    success_message = 'Trading Plan Updated Successfully'
    template_name = 'investment/trading_plan/index.html'

    def get_success_url(self):
        return reverse('trading_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trading_plan'] = TradingPlanModel.objects.all().order_by('name')
        return context


class TradingPlanDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = TradingPlanModel
    success_message = 'Trading Plan Deleted Successfully'
    fields = '__all__'
    template_name = 'investment/trading_plan/delete.html'
    context_object_name = "trading_plan"

    def get_success_url(self):
        return reverse('trading_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SignalPlanCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = SignalPlanModel
    form_class = SignalPlanForm
    success_message = 'Signal Plan Added Successfully'
    template_name = 'investment/signal_plan/index.html'

    def get_success_url(self):
        return reverse('signal_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signal_plan'] = SignalPlanModel.objects.all().order_by('name')
        return context


class SignalPlanListView(LoginRequiredMixin, ListView):
    model = SignalPlanModel
    fields = '__all__'
    template_name = 'investment/signal_plan/index.html'
    context_object_name = "signal_plan_list"

    def get_queryset(self):
        return SignalPlanModel.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SignalPlanForm
        return context


class SignalPlanDetailView(LoginRequiredMixin, DetailView):
    model = SignalPlanModel
    fields = '__all__'
    template_name = 'investment/signal_plan/detail.html'
    context_object_name = "signal_plan"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SignalPlanUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SignalPlanModel
    form_class = SignalPlanForm
    success_message = 'Signal Plan Updated Successfully'
    template_name = 'investment/signal_plan/index.html'

    def get_success_url(self):
        return reverse('signal_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signal_plan'] = SignalPlanModel.objects.all().order_by('name')
        return context


class SignalPlanDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = SignalPlanModel
    success_message = 'Signal Plan Deleted Successfully'
    fields = '__all__'
    template_name = 'investment/signal_plan/delete.html'
    context_object_name = "signal_plan"

    def get_success_url(self):
        return reverse('signal_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    
class MiningPlanCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = MiningPlanModel
    form_class = MiningPlanForm
    success_message = 'Mining Plan Added Successfully'
    template_name = 'investment/mining_plan/index.html'

    def get_success_url(self):
        return reverse('mining_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mining_plan'] = MiningPlanModel.objects.all().order_by('name')
        return context


class MiningPlanListView(LoginRequiredMixin, ListView):
    model = MiningPlanModel
    fields = '__all__'
    template_name = 'investment/mining_plan/index.html'
    context_object_name = "mining_plan_list"

    def get_queryset(self):
        return MiningPlanModel.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MiningPlanForm
        return context


class MiningPlanDetailView(LoginRequiredMixin, DetailView):
    model = MiningPlanModel
    fields = '__all__'
    template_name = 'investment/mining_plan/detail.html'
    context_object_name = "mining_plan"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class MiningPlanUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = MiningPlanModel
    form_class = MiningPlanForm
    success_message = 'Mining Plan Updated Successfully'
    template_name = 'investment/mining_plan/index.html'

    def get_success_url(self):
        return reverse('mining_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mining_plan'] = MiningPlanModel.objects.all().order_by('name')
        return context


class MiningPlanDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = MiningPlanModel
    success_message = 'Mining Plan Deleted Successfully'
    fields = '__all__'
    template_name = 'investment/mining_plan/delete.html'
    context_object_name = "mining_plan"

    def get_success_url(self):
        return reverse('mining_plan_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


