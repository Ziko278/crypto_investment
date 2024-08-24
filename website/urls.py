from django.urls import path
from website.views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='homepage'),
    path('about', AboutPageView.as_view(), name='about_us'),
    path('contact', ContactPageView.as_view(), name='contact_us'),
    path('terms-of-service', ServiceTermPageView.as_view(), name='service_term'),
    path('copy-expert-traders', TradeCopyPageView.as_view(), name='copy_trade'),
   ]

