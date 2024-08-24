from django.urls import path
from user_site.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('register', user_signup_view, name='register'),
    path('login', user_signin_view, name='login'),
    path('change-password', user_change_password_view, name='user_change_password'),
    path('logout', user_sign_out_view, name='logout'),

    path('password_reset/', password_reset_request, name='user_password_reset'),
    path('reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password_reset/done/', TemplateView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/done/', TemplateView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    path('profile/email-verification', email_verification_one, name='email_verify_1'),
    path('profile/send-verification-email', email_verification_two, name='email_verify_2'),
    path('profile/identity-verification', identity_verification, name='identity_verify'),
    path('profile/address-verification', address_verification, name='address_verify'),

    path('', UserDashboardView.as_view(), name='user_dashboard'),
    path('referrals', UserReferralView.as_view(), name='user_referral'),
    path('profile', UserProfileView.as_view(), name='user_profile'),
    path('profile/verification', UserProfileVerificationView.as_view(), name='user_profile_verification'),
    path('profile/<int:pk>/edit', UserProfileChangeView.as_view(), name='user_profile_edit'),

    path('plan/<str:plan>', UserPlanView.as_view(), name='user_plan_index'),

    path('funding/index', UserFundingListView.as_view(), name='user_funding_index'),
    path('funding/step1', user_funding_create_one, name='user_funding_create_1'),
    path('funding/step2', user_funding_create_two, name='user_funding_create_2'),
    path('funding/step3', user_funding_create_three, name='user_funding_create_3'),
    path('funding/<int:pk>/details', user_funding_create_four, name='user_funding_create_4'),
    path('funding/<int:pk>/upload-proof', FundingProofView.as_view(), name='user_funding_proof'),

    path('buy-crypto', UserBuyCryptoView.as_view(), name='user_buy_crypto'),
    path('watchlist', UserWatchListView.as_view(), name='user_watchlist'),
    path('watchlist/add', UserWatchListAddView.as_view(), name='user_watchlist_add'),
    path('watchlist/add/ajax', add_to_watchlist, name='user_watchlist_add_ajax'),
    path('watchlist/remove/ajax', remove_from_watchlist, name='user_watchlist_remove_ajax'),

    path('usd-to-crypto', usd_to_crypto_view, name='usd_to_crypto'),
    path('crypto-usd-to', crypto_to_usd_view, name='crypto_to_usd'),

    path('trade-room', TradeRoomView.as_view(), name='trade_room'),

    path('assets', UserAssetView.as_view(), name='user_asset_index'),
    path('asset/main', UserAssetMainView.as_view(), name='user_main_asset'),
    path('asset/all', UserAssetAllView.as_view(), name='user_all_asset'),
    path('asset/<str:name>/<str:symbol>', UserAssetDetailView.as_view(), name='user_asset_detail'),
    path('asset/buy', buy_asset_view, name='user_buy_asset'),
    path('asset/sell', sell_asset_view, name='user_sell_asset'),

    path('notifications', user_notification_list, name='user_notification_index'),

]

