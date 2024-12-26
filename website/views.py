from django.db.models import Sum
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from datetime import date, datetime, timedelta

from admin_site.models import SiteSettingModel
from investment.models import TradingPlanModel


class HomePageView(TemplateView):
    def get_template_names(self):
        # Get the first SiteSettingModel instance
        site_info = SiteSettingModel.objects.first()

        # Fallback in case no site settings are found
        if site_info is None:
            return ["website/template1/index.html"]

        # Dynamically determine the template based on site_info
        return [f"website/template{site_info.template}/index.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trading_plan_list'] = TradingPlanModel.objects.filter(status='active')
        return context


class AboutPageView(TemplateView):
    def get_template_names(self):
        # Get the first SiteSettingModel instance
        site_info = SiteSettingModel.objects.first()

        # Fallback in case no site settings are found
        if site_info is None:
            return ["website/template1/about.html"]

        # Dynamically determine the template based on site_info
        return [f"website/template{site_info.template}/about.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class ContactPageView(TemplateView):
    def get_template_names(self):
        # Get the first SiteSettingModel instance
        site_info = SiteSettingModel.objects.first()

        # Fallback in case no site settings are found
        if site_info is None:
            return ["website/template1/contact.html"]

        # Dynamically determine the template based on site_info
        return [f"website/template{site_info.template}/contact.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class TradeCopyPageView(TemplateView):
    def get_template_names(self):
        # Get the first SiteSettingModel instance
        site_info = SiteSettingModel.objects.first()

        # Fallback in case no site settings are found
        if site_info is None:
            return ["website/template1/trade_copy.html"]

        # Dynamically determine the template based on site_info
        return [f"website/template{site_info.template}/trade_copy.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class ServiceTermPageView(TemplateView):
    def get_template_names(self):
        # Get the first SiteSettingModel instance
        site_info = SiteSettingModel.objects.first()

        # Fallback in case no site settings are found
        if site_info is None:
            return ["website/template1/service_term.html"]

        # Dynamically determine the template based on site_info
        return [f"website/template{site_info.template}/service_term.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context
