import json

from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse, HttpRequest
from django.urls import reverse
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from admin_site.forms import SiteInfoForm, SiteSettingForm, CurrencyForm, SupportedCryptoForm
from admin_site.models import SiteInfoModel, SiteSettingModel, CurrencyModel, SupportedCryptoModel

from datetime import date, datetime, timedelta

from communication.models import UserNotificationModel
from communication.views import send_custom_email
from user_site.forms import UserFundingStatusForm, UserWithdrawalStatusForm
from user_site.models import UserFundingModel, UserTradeModel, UserWalletModel, UserProfileModel, UserWithdrawalModel
from user_site.views import crypto_to_usd_view, fetch_crypto_data


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_site/dashboard.html'

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(reverse('admin_login'))
        return super(AdminDashboardView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_user'] = UserProfileModel.objects.count()
        context['total_active_user'] = UserProfileModel.objects.filter(email_verified=True, identity_verified=True, address_verified=True).count()
        trading_balance = UserWalletModel.objects.all().aggregate(Sum('trading_balance'))[
            'trading_balance__sum']
        if trading_balance is None:
            trading_balance = 0
        context['total_trade_balance'] = trading_balance

        holding_balance = UserWalletModel.objects.all().aggregate(Sum('holding_balance'))[
            'holding_balance__sum']
        if holding_balance is None:
            holding_balance = 0
        context['total_holding_balance'] = holding_balance
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

    def dispatch(self, *args, **kwargs):
        if self.request.method == 'POST' and self.request.POST.get('status') == 'failed':
            reason_for_decline = self.request.POST.get('reason')
            funding = get_object_or_404(UserFundingModel, pk=self.kwargs.get('pk'))
            user_profile = get_object_or_404(UserProfileModel, user=funding.user)
            message = "Hi {}, Your funding of {} failed for the following reason: {}".format(
                user_profile.__str__(), funding.amount, reason_for_decline)
            notification = UserNotificationModel.objects.create(message=message, user=user_profile.user)
            notification.save()
        return super(FundingStatusChangeView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('funding_index', kwargs={'funding': self.object.status})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WithdrawalListView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_site/withdrawal/index.html'

    def dispatch(self, *args, **kwargs):
        withdrawal = self.kwargs.get('withdrawal')
        if withdrawal not in ['all', 'completed', 'pending', 'failed']:
            return redirect(reverse('withdrawal_index', kwargs={'withdrawal': 'all'}))

        return super(WithdrawalListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        withdrawal = self.kwargs.get('withdrawal')
        context['withdrawal'] = withdrawal
        if withdrawal == 'all':
            context['withdrawal_list'] = UserWithdrawalModel.objects.all().order_by('id').reverse()
        elif withdrawal == 'completed':
            context['withdrawal_list'] = UserWithdrawalModel.objects.filter(status='completed').order_by('id').reverse()
        elif withdrawal == 'pending':
            context['withdrawal_list'] = UserWithdrawalModel.objects.filter(status='pending').order_by('id').reverse()
        elif withdrawal == 'failed':
            context['withdrawal_list'] = UserWithdrawalModel.objects.filter(status='failed').order_by('id').reverse()
        return context


class WithdrawalStatusChangeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserWithdrawalModel
    form_class = UserWithdrawalStatusForm
    success_message = 'Status Updated'
    template_name = 'admin_site/withdrawal/index.html'

    def dispatch(self, *args, **kwargs):
        if self.request.method == 'POST':
            withdrawal = get_object_or_404(UserWithdrawalModel, pk=self.kwargs.get('pk'))
            user_profile = get_object_or_404(UserProfileModel, user=withdrawal.user)

            if self.request.POST.get('status') == 'failed':
                reason_for_decline = self.request.POST.get('reason')
                message = "Hi {}, Your withdrawal of {} failed for the following reason: {}".format(
                    user_profile.__str__(), withdrawal.amount, reason_for_decline)
            elif self.request.POST.get('status') == 'completed':
                message = "Hi {}, Your withdrawal of {} has been credited to your wallet".format(
                    user_profile.__str__(), withdrawal.amount)

            notification = UserNotificationModel.objects.create(message=message, user=user_profile.user)
            notification.save()
        return super(WithdrawalStatusChangeView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('withdrawal_index', kwargs={'withdrawal': self.object.status})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

def admin_sign_in_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            intended_route = request.POST.get('next') or request.GET.get('next')
            remember_me = request.POST.get('remember_me') or request.GET.get('remember_me')

            if user.is_superuser:
                login(request, user)
                messages.success(request, 'welcome back {}'.format(user.username.title()))
                if remember_me:
                    request.session.set_expiry(3600 * 24 * 30)
                else:
                    request.session.set_expiry(0)
                if intended_route:
                    return redirect(intended_route)
                return redirect(reverse('admin_dashboard'))

            else:
                messages.error(request, 'Unknown Identity, Access Denied')
                return redirect(reverse('login'))
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect(reverse('admin_login'))

    return render(request, 'admin_site/sign_in.html')


def admin_sign_out_view(request):
    logout(request)
    return redirect(reverse('admin_login'))


class TradeIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'admin_site/trade/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['open_trade_list'] = UserTradeModel.objects.filter(status='open').order_by('-created_at')
        context['close_trade_list'] = UserTradeModel.objects.filter(status='close').order_by('-created_at')
        return context


def close_ended_open_trade(request):
    open_trade_list = UserTradeModel.objects.filter(status='open')
    trade_count = 0

    for trade in open_trade_list:
        if trade:
            mock_request = HttpRequest()
            mock_request.GET = request.GET.copy()
            mock_request.GET['crypto'] = trade.name
            mock_request.GET['crypto_amount'] = trade.amount

            # Call the usd_to_crypto_view function directly
            json_response = crypto_to_usd_view(mock_request)
            data = json_response.content.decode('utf-8')
            data = json.loads(data)

            if 'price_in_usd' in data:
                current_amount = round(data.get('price_in_usd'), 2)
                if trade.direction == 'up':
                    trade.profit = ((current_amount - trade.open_value) * trade.amount/trade.open_value) * trade.leverage
                else:
                    trade.profit = ((trade.open_value - current_amount) * trade.amount/trade.open_value) * trade.leverage

                user_wallet = UserWalletModel.objects.get(user=trade.user)
                user_wallet.trading_balance += trade.amount + trade.profit
                user_wallet.save()

                trade.status = 'close'
                trade.close_value = current_amount
                trade.save()

    return HttpResponse(trade_count)


class SupportedCryptoCreateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = SupportedCryptoModel
    permission_required = 'admin_site.add_supportedcryptomodel'
    form_class = SupportedCryptoForm
    template_name = 'admin_site/supported_crypto/index.html'
    success_message = 'Crypto Payment Successfully Added'

    def get_success_url(self):
        return reverse('supported_crypto_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supported_crypto_list'] = SupportedCryptoModel.objects.all().order_by('name')
        return context


class SupportedCryptoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = SupportedCryptoModel
    permission_required = 'admin_site.add_supportedcryptomodel'
    fields = '__all__'
    template_name = 'admin_site/supported_crypto/index.html'
    context_object_name = "supported_crypto_list"

    def get_queryset(self):
        return SupportedCryptoModel.objects.all().order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SupportedCryptoForm
        context['crypto_list'] = fetch_crypto_data()
        return context


class SupportedCryptoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SupportedCryptoModel
    permission_required = 'admin_site.add_supportedcryptomodel'
    form_class = SupportedCryptoForm
    template_name = 'admin_site/supported_crypto/index.html'
    success_message = 'Crypto Payment Method Successfully Updated'

    def get_success_url(self):
        return reverse('supported_crypto_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SupportedCryptoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    model = SupportedCryptoModel
    permission_required = 'admin_site.add_supportedcryptomodel'
    fields = '__all__'
    template_name = 'admin_site/supported_crypto/delete.html'
    context_object_name = "supported_crypto"
    success_message = 'Crypto Payment Method Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('supported_crypto_index')