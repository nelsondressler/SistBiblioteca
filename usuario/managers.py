from django.contrib.auth.models import BaseUserManager

from django.utils.timezone import now
from django.db.transaction import atomic

class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):

        with atomic():
            user = self.model(email = self.normalize_email(email), last_login = now(), date_joined = now(), is_active = True, is_staff = is_staff, is_superuser = is_superuser, **extra_fields)
            user.set_password(password)
            user.save()

        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)
