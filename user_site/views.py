import json
import random
import re
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Sum, Q
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, JsonResponse, Http404, HttpRequest
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.messages.views import SuccessMessageMixin, messages
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from num2words import num2words

from admin_site.models import SiteInfoModel, SiteSettingModel, CurrencyModel, SupportedCryptoModel, AssetModel
from communication.models import UserNotificationModel
from communication.views import send_custom_email
from investment.models import TradingPlanModel, SignalPlanModel, MiningPlanModel

from user_site.forms import UserProfileForm, LoginForm, SignUpForm, UserFundingForm, UserFundingProofForm, \
    AssetConversionForm, UserProfileIdentityForm, UserProfileAddressForm, UserProfileEditForm, UserTradeForm, \
    UserWithdrawalMethodForm, UserWithdrawalForm
from user_site.models import UserProfileModel, UserFundingModel, UserWatchListModel, AssetConversionModel, \
    UserWalletModel, AssetValueModel, UserTradeModel, UserWithdrawalMethodModel, UserWithdrawalModel
import math


def round_to_sf(number, sf):
    if number == 0:
        return 0
    # Compute the factor for rounding
    factor = 10 ** (sf - int(math.floor(math.log10(abs(number)))) - 1)
    return round(number * factor) / factor


def user_signup_view(request):
    if request.method == 'POST':
        user_form = SignUpForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            if user.id and profile.id:
                referral_id = request.GET.get('user_id') or request.POST.get('user_id') or None
                if referral_id:
                    try:
                        referer = UserProfileModel.objects.get(user__username=referral_id)
                        referer.referrals.add(profile)
                        site_setting = SiteSettingModel.objects.first()
                        if site_setting.referral_payment_before_bonus:
                            referer_wallet = UserWalletModel.objects.get(user=referer.user)
                            referer_wallet.referral_balance += site_setting.referral_bonus
                            referer_wallet.save()
                    except Exception:
                        pass

                messages.success(request, 'Account Created Successfully')
                return redirect(reverse('login'))
    else:
        user_form = SignUpForm
        profile_form = UserProfileForm
    context = {
        'user_form': user_form,
        'user_id': request.GET.get('user_id', None),
        'profile_form': profile_form,
        'site_setting': SiteSettingModel.objects.first(),
        'currency_list': CurrencyModel.objects.filter(status='active'),
    }
    return render(request, 'user_site/register.html', context)


def user_signin_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # try to log user by either username or password
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    user = None
            if not user:
                messages.error(request, 'Invalid Username or Email ')

            else:
                username = user.username
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)

                        if 'remember_login' in request.POST:
                            request.session.set_expiry(0)
                            request.session.modified = True

                        user_profile = UserProfileModel.objects.get(user=request.user)
                        messages.success(request, 'Welcome Back {}'.format(user_profile.__str__()))
                        if not user_profile.email_verified:
                            return redirect(reverse('email_verify_1'))
                        if not user_profile.identity_verified and not user_profile.identity_verification_pending:
                            return redirect(reverse('identity_verify'))
                        if not user_profile.address_verified and not user_profile.address_verification_pending:
                            return redirect(reverse('address_verify'))

                        nxt = request.GET.get("next", None)
                        if nxt:
                            return redirect(request.GET.get('next'))
                        return redirect(reverse('user_dashboard'))
                    else:
                        messages.error(request, 'Account not Activated')
                else:
                    messages.error(request, 'Invalid Credentials')
        else:
            messages.error(request, 'Invalid Credentials')
    else:
        form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'user_site/login.html', context)


def user_sign_out_view(request):
    logout(request)
    return redirect(reverse('login'))


@login_required
def email_verification_one(request):
    user_profile = UserProfileModel.objects.get(user=request.user)
    if user_profile.email_verified:
        messages.warning(request, 'Email Account Already Verified')
        return redirect(reverse('user_profile'))

    return render(request, 'user_site/account/email_verify_1.html')


@login_required
def email_verification_two(request):
    user_profile = UserProfileModel.objects.get(user=request.user)
    if user_profile.email_verified:
        messages.warning(request, 'Email Account Already Verified')
        return redirect(reverse('user_profile'))

    if request.method == 'POST':
        user_code = request.POST.get('code').strip()
        if user_code == user_profile.last_verification_code:
            user_profile.email_verified = True
            user_profile.save()
            messages.success(request, 'Email Successfully Verified')
            if not user_profile.identity_verified:
                return redirect(reverse('identity_verify'))
            if not user_profile.address_verified:
                return redirect(reverse('address_verify'))
            return redirect(reverse('user_profile'))
        else:
            messages.error(request, 'Invalid Verification Code')
        context = {}
    else:
        site_info = SiteInfoModel.objects.first()
        code = random.randrange(10000, 100000)
        context = {
            'code': code,
            'profile': user_profile
        }
        mail_sent = send_custom_email(
            subject='Email Verification Email for {}'.format(site_info.name.title()),
            recipient_list=[request.user.username],
            template_name='communication/template/verify_email.html',
            context=context
        )

        user_profile.last_verification_code = code
        user_profile.save()
        if mail_sent:
            context['mail_sent'] = True
        else:
            context['mail_sent'] = False
    return render(request, 'user_site/account/email_verify_2.html', context)


@login_required
def identity_verification(request):
    user_profile = UserProfileModel.objects.get(user=request.user)
    if user_profile.identity_verified:
        messages.warning(request, 'User Identity Already Verified')
        return redirect(reverse('user_profile'))

    if request.method == 'POST':
        form = UserProfileIdentityForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            updated_profile.identity_verification_pending = True
            updated_profile.save()

            messages.success(request, 'Document submitted, Please await approval')

            if not user_profile.address_verified:
                return redirect(reverse('address_verify'))
            return redirect(reverse('user_profile'))
        else:
            messages.error(request, 'Please select a proper document')
    else:
        form = UserProfileIdentityForm(instance=user_profile)
    context = {
        'awaiting_approval': user_profile.identity_verification_pending,
        'form': form
    }
    return render(request, 'user_site/account/identity_verify.html', context)


@login_required
def address_verification(request):
    user_profile = UserProfileModel.objects.get(user=request.user)
    if user_profile.address_verified:
        messages.warning(request, 'User Address Already Verified')
        return redirect(reverse('user_profile'))

    if request.method == 'POST':
        form = UserProfileAddressForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            updated_profile = form.save(commit=False)
            updated_profile.address_verification_pending = True
            updated_profile.save()

            messages.success(request, 'Document submitted, Please await approval')

            return redirect(reverse('user_profile'))
        else:
            messages.error(request, 'Please select a proper document')

    context = {
        'awaiting_approval': user_profile.address_verification_pending,
        'user_profile': user_profile
    }
    return render(request, 'user_site/account/address_verify.html', context)


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        open_trade_list = UserTradeModel.objects.filter(user=self.request.user, status='open')
        context['open_trade_count'] = open_trade_list.count()
        context['open_trade_list'] = open_trade_list
        context['close_trade_list'] = UserTradeModel.objects.filter(user=self.request.user, status='close').order_by('id').reverse()[:5]
        context['asset_count'] = AssetValueModel.objects.filter(user=self.request.user, value__gt=0).count()
        return context


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfileModel.objects.get(user=self.request.user)
        context['user_profile'] = user
        context['form'] = UserProfileForm(instance=user)
        return context


class UserProfileChangeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserProfileModel
    template_name = 'user_site/account/profile.html'
    form_class = UserProfileEditForm
    success_message = 'Profile Successfully Updated'

    def get_success_url(self):
        return reverse('user_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfileModel.objects.get(user=self.request.user)
        context['user_profile'] = user
        context['form'] = UserProfileForm(instance=user)
        return context


class UserProfileVerificationView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/account/verification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfileModel.objects.get(user=self.request.user)
        context['user_profile'] = user
        return context


class UserReferralView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/account/referral.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserProfileModel.objects.get(user=self.request.user)
        context['user_profile'] = user_profile
        context['referral_link'] = reverse('register')
        context['domain'] = self.request.get_host()

        return context


@login_required
def user_change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        # Verify the current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Incorrect current password.')
            return redirect(reverse('user_change_password'))

        # Check if the new passwords match
        if len(new_password1) < 8:
            messages.error(request, 'Password must have at least 8 characters.')
            return redirect(reverse('user_change_password'))

        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d).+$", new_password1):
            messages.error(request, 'Password must contain both letters and numbers.')
            return redirect(reverse('user_change_password'))

        if new_password1 != new_password2:
            messages.error(request, 'New passwords do not match.')
            return redirect(reverse('user_change_password'))

        # Update the user's password
        user = request.user
        user.set_password(new_password1)
        user.save()

        # Update the user's session with the new password
        update_session_auth_hash(request, user)

        logout(request)

        messages.success(request, 'Password successfully changed. Please log in with the new password.')
        return redirect('login')

    return render(request, 'user_site/account/change_password.html')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_user = User.objects.filter(email=data).first()
            if associated_user:
                subject = "Password Reset Requested"
                email_template_name = "password_reset_email.html"
                context = {
                    "email": associated_user.email,
                    'domain': get_current_site(request).domain,
                    'site_name': 'Your site',
                    "uid": urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    "user": associated_user,
                    'token': default_token_generator.make_token(associated_user),
                    'protocol': 'http',
                }
                email = render_to_string(email_template_name, context)
                try:
                    send_mail(subject, email, 'your-email@gmail.com', [associated_user.email], fail_silently=False)
                except BadHeaderError:
                    messages.error(request, 'An Error has Occured, Try Later')
                    return redirect("password_reset")
                return redirect("password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request, "user_portal/password_reset.html", {"password_reset_form": password_reset_form})


def password_reset_confirm(request, uidb64=None, token=None):
    logout(request)
    if request.method == 'POST':
        form = SetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('password_reset_complete')
    else:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user=user)
        else:
            return HttpResponse('Password reset link is invalid.')

    return render(request, 'password_reset_confirm.html', {'form': form})


class UserPlanView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/investment/plan.html'

    def dispatch(self, *args, **kwargs):
        plan = self.kwargs.get('plan')
        if plan not in ['all', 'trading', 'mining', 'signal']:
            return redirect(reverse('user_plan', kwargs={'plan': 'all'}))

        return super(UserPlanView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plan'] = self.kwargs.get('plan')
        context['trading_plan_list'] = TradingPlanModel.objects.filter(status='active')
        context['signal_plan_list'] = SignalPlanModel.objects.filter(status='active')
        context['mining_plan_list'] = MiningPlanModel.objects.filter(status='active')
        return context


class UserFundingListView(LoginRequiredMixin, ListView):
    model = UserFundingModel
    fields = '__all__'
    template_name = 'user_site/funding/index.html'
    context_object_name = "funding_list"

    def get_queryset(self):
        return UserFundingModel.objects.filter(user=self.request.user).order_by('id').reverse()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@login_required
def user_funding_create_one(request):
    if request.method == 'POST':
        amount = request.POST.get('amount', 0)
        account = request.POST.get('account')

        if 'trade_plan' in request.POST:
            trading_plan = request.POST.get('trade_plan')
            url = f"{reverse('user_funding_create_2')}?amount={amount}&account={account}&trade_plan={trading_plan}"
        else:
            url = f"{reverse('user_funding_create_2')}?amount={amount}&account={account}"
        return redirect(url)
    context = {}
    if 'trade_plan' in request.GET:
        trade_id = request.GET.get('trade_plan')
        try:
            plan = TradingPlanModel.objects.get(pk=trade_id)
            context['amount'] = plan.amount
            context['trade_plan'] = trade_id
            context['is_trading'] = True
        except Exception:
            pass
    return render(request, 'user_site/funding/step_1.html', context)


@login_required
def user_funding_create_two(request):
    pay = request.GET.get('pay', 'no')
    account = request.GET.get('account')
    amount = request.GET.get('amount')
    if pay == 'yes':
        if 'trade_plan' in request.GET:
            trading_plan = request.GET.get('trade_plan')
            url = f"{reverse('user_funding_create_3')}?amount={amount}&account={account}&trade_plan={trading_plan}"
        else:
            url = f"{reverse('user_funding_create_3')}?amount={amount}&account={account}"
        return redirect(url)

    context = {
        'account': account,
        'amount': amount,
        'amount_in_word': num2words(amount),
        'trade_plan': request.GET.get('trade_plan', None)
    }
    return render(request, 'user_site/funding/step_2.html', context=context)


@login_required
def user_funding_create_three(request):
    account = request.GET.get('account')
    amount = request.GET.get('amount')
    form = UserFundingForm()
    if request.method == 'POST':
        form = UserFundingForm(request.POST)
        if form.is_valid():
            funding = form.save()
            if funding.id:
                if 'trade_plan' in request.POST:
                    trade_id = request.POST.get('trade_plan')
                    try:
                        trade_plan = TradingPlanModel.objects.get(pk=trade_id)
                        if trade_plan.amount == funding.amount:
                            user_profile = UserProfileModel.objects.get(user=request.user)
                            user_profile.trade_plan = trade_plan
                            user_profile.save()
                    except Exception:
                        pass
                return redirect(reverse('user_funding_create_4', kwargs={'pk': funding.id}))
            else:
                messages.error(request, 'Error Processing Request, Try Again')

    context = {
        'account': account,
        'amount': amount,
        'amount_in_word': num2words(amount),
        'supported_crypto_list': SupportedCryptoModel.objects.filter(status='active'),
        'trade_plan': request.GET.get('trade_plan', None),
        'form': form
    }
    return render(request, 'user_site/funding/step_3.html', context=context)


@login_required
def user_funding_create_four(request, pk):
    funding = get_object_or_404(UserFundingModel, pk=pk)
    if funding.user != request.user:
        messages.error(request, 'Access Denied')
        return redirect(reverse('user_funding_index'))

    created_at = funding.created_at  # Ensure this is in UTC

    # Calculate the target end time (60 minutes after created_at)
    target_time = created_at + timedelta(minutes=60)

    context = {
        'funding': funding,
        'created_at': created_at,
        'target_time': target_time
    }
    return render(request, 'user_site/funding/step_4.html', context=context)


class FundingProofView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UserFundingModel
    form_class = UserFundingProofForm
    success_message = 'Proof Uploaded, Please wait for Confirmation'
    template_name = 'user_site/funding/step_1.html'

    def get_success_url(self):
        return reverse('user_funding_create_4', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserBuyCryptoView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/investment/buy_crypto.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def fetch_crypto_data():
    url = 'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []


def fetch_single_crypto_data(crypto_id):
    url = f'https://api.coingecko.com/api/v3/coins/markets'
    params = {
        'vs_currency': 'usd',
        'ids': crypto_id,  # Specify the ID of the cryptocurrency
        'order': 'market_cap_desc',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []


class UserWatchListAddView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/investment/watchlist_add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crypto_list'] = fetch_crypto_data()
        watch_list = UserWatchListModel.objects.get(user=self.request.user).watch_lists.all()
        context['user_watch_list'] = [asset.symbol for asset in watch_list]

        return context


def add_to_watchlist(request):
    name = request.GET.get('name', None)
    symbol = request.GET.get('symbol', None)
    category = request.GET.get('symbol', 'crypto')

    if name and symbol:
        try:
            asset = AssetModel.objects.get(name=name, symbol=symbol, category=category)
        except Exception:
            asset = AssetModel.objects.create(name=name, symbol=symbol, category=category)

        watch_list = UserWatchListModel.objects.get(user=request.user)
        if asset in watch_list.watch_lists.all():
            return HttpResponse('{} Already Added'.format(name.title()))
        watch_list.watch_lists.add(asset)
        return HttpResponse('{} Added To Watch List'.format(name.title()))
    return HttpResponse('An Error Occurred')


def remove_from_watchlist(request):
    name = request.GET.get('name', None)
    symbol = request.GET.get('symbol', None)

    if name and symbol:
        try:
            asset = AssetModel.objects.get(name=name, symbol=symbol)
        except Exception:
            return HttpResponse('An Error Occurred')

        watch_list = UserWatchListModel.objects.get(user=request.user)
        if asset in watch_list.watch_lists.all():
            watch_list.watch_lists.remove(asset)
            return HttpResponse('{} Removed'.format(name.title()))

    return HttpResponse('An Error Occurred')


class UserWatchListView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/investment/watchlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crypto_list'] = fetch_crypto_data()
        watch_list = UserWatchListModel.objects.get(user=self.request.user).watch_lists.all()
        context['user_watch_list'] = [asset.symbol for asset in watch_list]
        return context


def usd_to_crypto_view(request):
    # Define the cryptocurrency and the USD amount
    crypto_currency = request.GET.get('crypto', 'bitcoin')  # default to bitcoin
    usd_amount = float(request.GET.get('usd_amount', 0))  # default to 100 USD

    # Fetch the current price of the cryptocurrency in USD
    api_url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_currency}&vs_currencies=usd'
    response = requests.get(api_url)

    # Check if the API call was successful
    if response.status_code == 200:
        data = response.json()
        price_in_usd = data.get(crypto_currency, {}).get('usd', 0)

        # Calculate how much crypto can be bought with the given USD amount
        if price_in_usd > 0:
            crypto_amount = usd_amount / price_in_usd
        else:
            crypto_amount = 0

        # Return the result as JSON
        return JsonResponse({
            'crypto_currency': crypto_currency,
            'usd_amount': usd_amount,
            'price_in_usd': price_in_usd,
            'crypto_amount': crypto_amount,
            'status': 'success'
        })
    else:
        # Handle errors (e.g., invalid cryptocurrency)
        return JsonResponse({'status': 'error',
                             'error': 'Could not fetch the cryptocurrency price'}, status=400)


def crypto_to_usd_view(request):
    # Define the cryptocurrency and the amount
    crypto_currency = request.GET.get('crypto', 'bitcoin')  # default to bitcoin
    crypto_amount = float(request.GET.get('crypto_amount', 0))  # default to 0 crypto

    # Fetch the current price of the cryptocurrency in USD
    api_url = f'https://api.coingecko.com/api/v3/simple/price?ids={crypto_currency}&vs_currencies=usd'
    response = requests.get(api_url)

    # Check if the API call was successful
    if response.status_code == 200:
        data = response.json()
        price_in_usd = data.get(crypto_currency, {}).get('usd', 0)

        # Calculate how much USD the given amount of crypto is worth
        if price_in_usd > 0:
            usd_amount = crypto_amount * price_in_usd
        else:
            usd_amount = 0

        # Return the result as JSON
        return JsonResponse({
            'crypto_currency': crypto_currency,
            'crypto_amount': crypto_amount,
            'price_in_usd': price_in_usd,
            'usd_amount': usd_amount,
            'status': 'success'
        })
    else:
        # Handle errors (e.g., invalid cryptocurrency)
        return JsonResponse({'status': 'error',
                             'error': 'Could not fetch the cryptocurrency price'}, status=400)


class UserAssetMainView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/asset/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class UserAssetAllView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/asset/all_asset.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crypto_list'] = fetch_crypto_data()

        return context


class UserAssetDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/asset/asset_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['symbol'] = self.kwargs.get('symbol')
        name = self.kwargs.get('name')
        context['name'] = name
        try:
            crypto_wallet = AssetValueModel.objects.get(user=self.request.user, name=name)
            context['crypto_value'] = round_to_sf(crypto_wallet.value, 3)
        except AssetValueModel.DoesNotExist:
            context['crypto_value'] = 0.0

        return context


class UserAssetView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/asset/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_list'] = AssetValueModel.objects.filter(user=self.request.user)
        return context


@login_required
def buy_asset_view(request):
    if request.method == 'POST':
        form = AssetConversionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get('amount')
            user_wallet = UserWalletModel.objects.get(user=request.user)
            if user_wallet.holding_balance < amount:
                messages.error(request, 'Insufficient Funds, Please fund your account and try again')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            mock_request = HttpRequest()
            mock_request.GET = request.GET.copy()
            mock_request.GET['crypto'] = form.cleaned_data['name']
            mock_request.GET['usd_amount'] = form.cleaned_data.get('amount')

            # Call the usd_to_crypto_view function directly
            json_response = usd_to_crypto_view(mock_request)
            data = json_response.content.decode('utf-8')
            data = json.loads(data)

            if 'crypto_amount' in data:
                conversion = form.save(commit=False)
                conversion.direction = 'crypto'
                conversion.user = request.user
                conversion.value = round_to_sf(data.get('crypto_amount'), 3)
                conversion.save()

                user_wallet.holding_balance -= amount
                user_wallet.save()

                messages.success(request, 'Asset Conversion Successful')
            else:
                messages.error(request, 'An Error Occurred,Try Later')
        else:
            messages.error(request, 'An Error Occurred,Try Later')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def sell_asset_view(request):
    if request.method == 'POST':
        form = AssetConversionForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data.get('value')
            crypto = form.cleaned_data.get('name')
            try:
                crypto_wallet = AssetValueModel.objects.get(user=request.user, name=crypto)
                if crypto_wallet.value < value:
                    messages.error(request, 'Insufficient Funds, Please fund your account and try again')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            except AssetValueModel.DoesNotExist:
                messages.error(request, 'Insufficient Funds, Please fund your account and try again')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            mock_request = HttpRequest()
            mock_request.GET = request.GET.copy()
            mock_request.GET['crypto'] = crypto
            mock_request.GET['crypto_amount'] = value

            # Call the usd_to_crypto_view function directly
            json_response = crypto_to_usd_view(mock_request)
            data = json_response.content.decode('utf-8')
            data = json.loads(data)

            if 'usd_amount' in data:
                user_wallet = UserWalletModel.objects.get(user=request.user)

                conversion = form.save(commit=False)
                conversion.direction = 'cash'
                conversion.user = request.user
                conversion.amount = round(data.get('usd_amount'), 2)
                conversion.save()

                user_wallet.holding_balance += conversion.amount
                user_wallet.save()

                messages.success(request, 'Asset Conversion Successful')
            else:
                messages.error(request, 'An Error Occurred,Try Later')
        else:
            messages.error(request, 'An Error Occurred,Try Later')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def user_notification_list(request):
    new_notification_list = UserNotificationModel.objects.filter(user=request.user, is_read=False)
    for notification in new_notification_list:
        notification.is_read = True
        notification.save()
    context = {
        'notification_list': UserNotificationModel.objects.filter(user=request.user).order_by('id').reverse()
    }
    return render(request, 'user_site/notification/index.html', context)


class UserTradePageListView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/trade/market_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfileModel.objects.get(user=self.request.user)
        context['user_profile'] = user
        context['crypto_list'] = fetch_crypto_data()
        return context


class TradeRoomView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/trade/trade_room.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['symbol'] = self.request.GET.get('symbol')
        context['name'] = self.request.GET.get('name')
        context['category'] = self.request.GET.get('category')
        return context


def trade_create_view(request):
    if request.method == 'POST':
        form = UserTradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            mock_request = HttpRequest()
            mock_request.GET = request.GET.copy()
            mock_request.GET['crypto'] = form.cleaned_data.get('name')
            mock_request.GET['crypto_amount'] = form.cleaned_data.get('amount')

            # Call the usd_to_crypto_view function directly
            json_response = crypto_to_usd_view(mock_request)
            data = json_response.content.decode('utf-8')
            data = json.loads(data)

            if 'price_in_usd' in data:
                trade.open_value = round(data.get('price_in_usd'), 2)

            user_wallet = UserWalletModel.objects.get(user=request.user)
            user_wallet.trading_balance -= trade.amount
            user_wallet.save()

            trade.save()

            messages.success(request, 'Trade Placed Successfully')
            return redirect(reverse('user_trade_detail', kwargs={'pk': trade.id}))


class UserTradeIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'user_site/trade/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['open_trade_list'] = UserTradeModel.objects.filter(user=self.request.user, status='open')
        context['close_trade_list'] = UserTradeModel.objects.filter(user=self.request.user, status='close')
        return context


class UserTradeDetailView(LoginRequiredMixin, DetailView):
    template_name = 'user_site/trade/detail.html'
    model = UserTradeModel
    fields = '__all__'
    context_object_name = "trade"

    def dispatch(self, *args, **kwargs):
        trade = get_object_or_404(UserTradeModel, pk=self.kwargs.get('pk'))
        if self.request.user != trade.user:
            messages.error(self.request, 'Access Denied')
            return redirect(reverse('user_dashboard'))

        return super(UserTradeDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['crypto'] = fetch_single_crypto_data(self.object.name)[0]
        return context


def user_close_trade_view(request, pk):
    trade = get_object_or_404(UserTradeModel, pk=pk)
    if trade.status != 'open' or trade.user != request.user:
        messages.error(request, 'Access Denied')
        return redirect(reverse('user_dashboard'))

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

        messages.success(request, 'Trade Closed')
        return redirect(reverse('user_trade_detail', kwargs={'pk': trade.id}))

    messages.error(request, 'An Error Occurred')
    return redirect(reverse('user_trade_detail', kwargs={'pk': trade.id}))


class WithdrawalMethodCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserWithdrawalMethodModel
    form_class = UserWithdrawalMethodForm
    success_message = 'Withdrawal Method Added Successfully'
    template_name = 'user_site/withdrawal_method/index.html'

    def get_success_url(self):
        return reverse('withdrawal_method_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['withdrawal_method'] = UserWithdrawalMethodModel.objects.all().order_by('name')
        return context


class WithdrawalMethodListView(LoginRequiredMixin, ListView):
    model = UserWithdrawalMethodModel
    fields = '__all__'
    template_name = 'user_site/withdrawal_method/index.html'
    context_object_name = "withdrawal_method_list"

    def get_queryset(self):
        return UserWithdrawalMethodModel.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserWithdrawalMethodForm
        context['supported_crypto_list'] = SupportedCryptoModel.objects.filter(status='active')
        return context


class WithdrawalMethodDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = UserWithdrawalMethodModel
    success_message = 'Withdrawal Method Deleted Successfully'
    fields = '__all__'
    template_name = 'user_site/withdrawal_method/delete.html'
    context_object_name = "withdrawal_method"

    def dispatch(self, *args, **kwargs):
        method = get_object_or_404(UserWithdrawalMethodModel, pk=self.kwargs.get('pk'))
        if method.user != self.request.user:
            messages.error(self.request, 'Access Denied')
            return redirect(reverse('user_dashboard'))

        return super(WithdrawalMethodDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('withdrawal_method_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WithdrawalCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = UserWithdrawalModel
    form_class = UserWithdrawalForm
    success_message = 'Withdrawal Applied Successfully, Wait for Approval'
    template_name = 'user_site/withdrawal/create.html'

    def dispatch(self, *args, **kwargs):
        user_profile = get_object_or_404(UserProfileModel, user=self.request.user)
        if not user_profile.email_verified:
            messages.error(self.request, 'Verify Email to before withdrawal')
            return redirect(reverse('email_verify_1'))

        if not user_profile.identity_verified:
            messages.error(self.request, 'Verify Identity to before withdrawal')
            return redirect(reverse('identity_verify'))

        if not user_profile.address_verified:
            messages.error(self.request, 'Verify Address to before withdrawal')
            return redirect(reverse('address_verify'))

        return super(WithdrawalCreateView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('withdrawal_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['withdrawal_method_list'] = UserWithdrawalMethodModel.objects.filter(user=self.request.user)
        return context


class WithdrawalListView(LoginRequiredMixin, ListView):
    model = UserWithdrawalModel
    fields = '__all__'
    template_name = 'user_site/withdrawal/index.html'
    context_object_name = "withdrawal_list"

    def get_queryset(self):
        return UserWithdrawalModel.objects.filter(user=self.request.user).order_by('id').reverse()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class WithdrawalDetailView(LoginRequiredMixin, DetailView):
    model = UserWithdrawalModel
    fields = '__all__'
    template_name = 'user_site/withdrawal/detail.html'
    context_object_name = "withdrawal"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


# Sample names list with approximately 50 names
names = [
    "John K.", "Alice M.", "Robert T.", "Maria S.", "James P.",
    "Laura J.", "Michael D.", "Emma R.", "David L.", "Sophia N.",
    "Chris W.", "Olivia J.", "Daniel R.", "Emily B.", "Matthew H.",
    "Charlotte C.", "Lucas M.", "Ava G.", "Ethan S.", "Mia T.",
    "Liam A.", "Isabella F.", "Noah Z.", "Amelia Y.", "Jacob X.",
    "Harper Q.", "Logan V.", "Ella O.", "Jackson K.", "Grace P.",
    "Aiden D.", "Chloe N.", "Carter R.", "Scarlett E.", "Gavin J.",
    "Zoe L.", "Isaiah F.", "Aria B.", "Samuel H.", "Sofia M.",
    "Anthony D.", "Madison J.", "Levi K.", "Victoria P.", "Elijah W.",
    "Lily C.", "Caleb Y.", "Layla Q.", "Henry N.", "Natalie Z."
]


def random_transaction(request):
    # Pick a random name
    name = random.choice(names)

    # Pick a random amount (multiple of 5 between 50 and 1000)
    amount = random.randint(10, 200) * 5  # (10 to 200, so multiples of 5 are between 50 and 1000)

    # Randomly choose between deposit or withdrawal
    transaction_type = random.choice(['deposited', 'withdrew'])

    # Create the response string
    message = f"{name} just {transaction_type} ${amount}."

    return JsonResponse({'message': message, 'status': transaction_type})
