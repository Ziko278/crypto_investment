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
from admin_site.forms import SiteInfoForm, SiteSettingForm, CurrencyForm
from admin_site.models import SiteInfoModel, SiteSettingModel, CurrencyModel

from datetime import date, datetime, timedelta

from user_site.forms import UserFundingStatusForm
from user_site.models import UserFundingModel


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_site/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SiteInfoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SiteInfoModel
    form_class = SiteInfoForm
    permission_required = 'admin_site.change_siteinfomodel'
    success_message = 'Site Information Updated Successfully'
    template_name = 'admin_site/site_info/create.html'

    def dispatch(self, *args, **kwargs):
        site_info = SiteInfoModel.objects.first()
        if not site_info:
            return super(SiteInfoCreateView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('site_info_edit', kwargs={'pk': site_info.pk}))

    def get_success_url(self):
        return reverse('site_info_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SiteInfoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = SiteInfoModel
    permission_required = 'admin_site.view_siteinfomodel'
    fields = '__all__'
    template_name = 'admin_site/site_info/detail.html'
    context_object_name = "site_info"

    def dispatch(self, *args, **kwargs):
        site_info = SiteInfoModel.objects.first()
        if site_info:
            if self.kwargs.get('pk') != site_info.id:
                return redirect(reverse('site_info_detail', kwargs={'pk': site_info.pk}))
            return super(SiteInfoDetailView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('site_info_create'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SiteInfoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SiteInfoModel
    permission_required = 'admin_site.change_siteinfomodel'
    form_class = SiteInfoForm
    success_message = 'Site Information Updated Successfully'
    template_name = 'admin_site/site_info/create.html'

    def get_success_url(self):
        return reverse('site_info_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_info'] = self.object
        return context


class SiteSettingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SiteSettingModel
    form_class = SiteSettingForm
    permission_required = 'admin_site.change_sitesettingmodel'
    success_message = 'Site Setting Updated Successfully'
    template_name = 'admin_site/site_setting/create.html'

    def dispatch(self, *args, **kwargs):
        site_info = SiteSettingModel.objects.first()
        if not site_info:
            return super(SiteSettingCreateView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('site_setting_edit', kwargs={'pk': site_info.pk}))

    def get_success_url(self):
        return reverse('site_setting_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SiteSettingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = SiteSettingModel
    permission_required = 'admin_site.change_sitesettingmodel'
    fields = '__all__'
    template_name = 'admin_site/site_setting/detail.html'
    context_object_name = "site_setting"

    def dispatch(self, *args, **kwargs):
        site_info = SiteSettingModel.objects.first()
        if site_info:
            if self.kwargs.get('pk') != site_info.id:
                return redirect(reverse('site_setting_detail', kwargs={'pk': site_info.pk}))
            return super(SiteSettingDetailView, self).dispatch(*args, **kwargs)
        else:
            return redirect(reverse('site_setting_create'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class SiteSettingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SiteSettingModel
    form_class = SiteSettingForm
    permission_required = 'admin_site.change_sitesettingmodel'
    success_message = 'Site Setting Updated Successfully'
    template_name = 'admin_site/site_setting/create.html'

    def get_success_url(self):
        return reverse('site_setting_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_setting'] = self.object
        return context


class CurrencyCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = CurrencyModel
    permission_required = 'admin_site.add_currencymodel'
    form_class = CurrencyForm
    template_name = 'admin_site/currency/index.html'
    success_message = 'Currency Successfully Added'

    def get_success_url(self):
        return reverse('currency_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['currency_list'] = CurrencyModel.objects.all().order_by('name')
        return context


class CurrencyListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = CurrencyModel
    permission_required = 'admin_site.add_currencymodel'
    fields = '__all__'
    template_name = 'admin_site/currency/index.html'
    context_object_name = "currency_list"

    def get_queryset(self):
        return CurrencyModel.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CurrencyForm
        return context


class CurrencyUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CurrencyModel
    permission_required = 'admin_site.add_currencymodel'
    form_class = CurrencyForm
    template_name = 'admin_site/currency/index.html'
    success_message = 'Currency Successfully Updated'

    def get_success_url(self):
        return reverse('currency_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CurrencyDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = CurrencyModel
    permission_required = 'admin_site.add_currencymodel'
    fields = '__all__'
    template_name = 'admin_site/currency/delete.html'
    context_object_name = "currency"
    success_message = 'Currency Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('currency_index')


class FundingListView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_site/funding/index.html'

    def dispatch(self, *args, **kwargs):
        funding = self.kwargs.get('funding')
        if funding not in ['all', 'completed', 'pending', 'failed']:
            return redirect(reverse('funding_index', kwargs={'funding': 'all'}))

        return super(FundingListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funding = self.kwargs.get('funding')
        context['funding'] = funding
        if funding == 'all':
            context['funding_list'] = UserFundingModel.objects.all().order_by('id').reverse()
        elif funding == 'completed':
            context['funding_list'] = UserFundingModel.objects.filter(status='completed').order_by('id').reverse()
        elif funding == 'pending':
            context['funding_list'] = UserFundingModel.objects.filter(status='pending').order_by('id').reverse()
        elif funding == 'failed':
            context['funding_list'] = UserFundingModel.objects.filter(status='failed').order_by('id').reverse()
        return context


class FundingStatusChangeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserFundingModel
    form_class = UserFundingStatusForm
    success_message = 'Status Updated'
    template_name = 'admin_site/funding/index.html'

    def get_success_url(self):
        return reverse('funding_index', kwargs={'funding': self.object.status})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
