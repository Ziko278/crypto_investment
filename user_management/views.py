from django.contrib.auth.decorators import login_required
from django.db.models.functions import Lower
from django.shortcuts import render, redirect, get_object_or_404
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

from communication.models import UserNotificationModel
from investment.models import *
from investment.forms import *
from user_site.models import UserProfileModel


class UserListView(LoginRequiredMixin, ListView):
    model = User
    fields = '__all__'
    template_name = 'user_management/user/index.html'
    context_object_name = "user_list"

    def get_queryset(self):
        return User.objects.filter(is_superuser=False).order_by(Lower('username'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    fields = '__all__'
    template_name = 'user_management/user/detail.html'
    context_object_name = "client"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    success_message = 'User Deleted Successfully'
    template_name = 'user_management/user/delete.html'
    context_object_name = "client"

    def get_success_url(self):
        return reverse('admin_user_index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class PendingUserListView(LoginRequiredMixin, TemplateView):
    template_name = 'user_management/user/pending_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_email_list'] = UserProfileModel.objects.filter(email_verified=False)
        context['pending_identity_list'] = UserProfileModel.objects.filter(identity_verified=False, identity_verification_pending=True)
        context['pending_address_list'] = UserProfileModel.objects.filter(address_verified=False, address_verification_pending=True)
        return context


@login_required
def confirm_identity_verification(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied for current User')
        return redirect(reverse('user_dashboard'))
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfileModel, pk=pk)
        status = request.POST.get('status')
        if status == 'confirm':
            user_profile.identity_verified = True
            user_profile.identity_verification_pending = False
            user_profile.save()
            messages.success(request, 'User Identity marked as Verified')

        if status == 'decline':
            user_profile.identity_verification_pending = False
            user_profile.identity_document_1 = None
            user_profile.identity_document_2 = None

            user_profile.save()
            messages.success(request, 'User Identity Verification Declined')

            reason_for_decline = request.POST.get('reason')
            message = "Hi {}, Your Identity verification failed for the following reason: {}".format(user_profile.__str__(), reason_for_decline)
            notification = UserNotificationModel.objects.create(message=message, user=user_profile.user)
            notification.save()

        return redirect(reverse('admin_user_detail', kwargs={'pk': user_profile.user.id}))

    return redirect(reverse('admin_pending_user_index'))


@login_required
def confirm_address_verification(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Access Denied for current User')
        return redirect(reverse('user_dashboard'))
    if request.method == 'POST':
        user_profile = get_object_or_404(UserProfileModel, pk=pk)
        status = request.POST.get('status')
        if status == 'confirm':
            user_profile.address_verified = True
            user_profile.address_verification_pending = False
            user_profile.save()
            messages.success(request, 'User Address marked as Verified')

        if status == 'decline':
            user_profile.address_verification_pending = False
            user_profile.address_document = None

            user_profile.save()
            messages.success(request, 'User Address Verification Declined')

            reason_for_decline = request.POST.get('reason')
            message = "Hi {}, Your address verification failed for the following reason: {}".format(user_profile.__str__(), reason_for_decline)
            notification = UserNotificationModel.objects.create(message=message, user=user_profile.user)
            notification.save()

        return redirect(reverse('admin_user_detail', kwargs={'pk': user_profile.user.id}))

    return redirect(reverse('admin_pending_user_index'))


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'user_management/user/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = UserProfileModel.objects.all().count()
        context['total_verified_users'] = UserProfileModel.objects.filter(email_verified=True, identity_verified=True, address_verified=True).count()
        return context
