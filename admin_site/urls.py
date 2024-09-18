from django.urls import path
from admin_site.views import *

urlpatterns = [
    path('', AdminDashboardView.as_view(), name='admin_dashboard'),
    path('login', admin_sign_in_view, name='admin_login'),
    path('logout', admin_sign_out_view, name='admin_logout'),
    
    path('site-info/create', SiteInfoCreateView.as_view(), name='site_info_create'),
    path('site-info/<int:pk>/detail', SiteInfoDetailView.as_view(), name='site_info_detail'),
    path('site-info/<int:pk>/edit', SiteInfoUpdateView.as_view(), name='site_info_edit'),

    path('site-setting/create', SiteSettingCreateView.as_view(), name='site_setting_create'),
    path('site-setting/<int:pk>/detail', SiteSettingDetailView.as_view(), name='site_setting_detail'),
    path('site-setting/<int:pk>/edit', SiteSettingUpdateView.as_view(), name='site_setting_edit'),
    
    path('currency/create', CurrencyCreateView.as_view(), name='currency_create'),
    path('currency/index', CurrencyListView.as_view(), name='currency_index'),
    path('currency/<int:pk>/edit', CurrencyUpdateView.as_view(), name='currency_edit'),
    path('currency/<int:pk>/delete', CurrencyDeleteView.as_view(), name='currency_delete'),

    path('funding/<str:funding>/index', FundingListView.as_view(), name='funding_index'),
    path('funding/<int:pk>/update-status', FundingStatusChangeView.as_view(), name='funding_update_status'),

    path('withdrawal/<str:withdrawal>/index', WithdrawalListView.as_view(), name='withdrawal_index'),
    path('withdrawal/<int:pk>/update-status', WithdrawalStatusChangeView.as_view(), name='withdrawal_update_status'),

    path('trades', TradeIndexView.as_view(), name='trade_index'),

    path('trade/close-completed', close_ended_open_trade, name='funding_update_status'),

]

