from django.core.management.base import BaseCommand
from admin_site.views import close_ended_open_trade_cron  # Adjust this as needed
from django.http import HttpRequest


class Command(BaseCommand):
    help = 'Automatically settle pending Trades'

    def handle(self, *args, **kwargs):
        request = HttpRequest()
        updated_match = close_ended_open_trade_cron(request)  # Call your function
