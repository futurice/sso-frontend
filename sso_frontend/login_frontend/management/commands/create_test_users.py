from django.core.management.base import BaseCommand
from login_frontend.models import User
from django.utils import timezone
import datetime


class Command(BaseCommand):
    args = ''
    help = 'Creates two test users, test and test_admin to the database for local development'

    def handle(self, *args, **options):
        test = User()
        test.username = 'test'
        test.email = 'test@test.com'
        test.primary_phone = '0000000000'
        test.primary_phone_refresh = timezone.make_aware(datetime.datetime.now())
        test.save()
        print "User 'test' added to the database"

        test_admin = User()
        test_admin.username = 'test_admin'
        test_admin.email = 'test_admin@test.com'
        test_admin.primary_phone = '11111111111'
        test_admin.primary_phone_refresh = timezone.make_aware(datetime.datetime.now())
        test_admin.is_admin = True
        test_admin.save()
        print "User 'test_admin' added to the database'"


