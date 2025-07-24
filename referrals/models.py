from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets
import string


class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(phone, password, **extra_fields)


class User(AbstractUser):
    username = None
    phone = models.CharField(max_length=15, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_invite_code()
        super().save(*args, **kwargs)

    @classmethod
    def generate_invite_code(cls):
        while True:
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not cls.objects.filter(invite_code=code).exists():
                return code

    def __str__(self):
        return self.phone