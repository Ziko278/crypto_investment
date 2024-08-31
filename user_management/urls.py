from django.urls import path
from user_management.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path('index', UserListView.as_view(), name='admin_user_index'),
    path('<int:pk>/detail', UserDetailView.as_view(), name='admin_user_detail'),
    path('<int:pk>/delete', UserDeleteView.as_view(), name='admin_user_delete'),

    path('pending-verifications', PendingUserListView.as_view(), name='admin_pending_user_index'),
    path('identity/<int:pk>/verify', confirm_identity_verification, name='confirm_identity_verification'),
    path('address/<int:pk>/verify', confirm_address_verification, name='confirm_address_verification'),

    path('dashboard', UserDashboardView.as_view(), name='admin_user_dashboard'),

]

