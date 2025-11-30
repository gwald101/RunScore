from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, firebase_uid, password=None, **extra_fields):
        if not firebase_uid:
            raise ValueError('Firebase UID is required')
        user = self.model(firebase_uid=firebase_uid, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, firebase_uid, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(firebase_uid, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    firebase_uid = models.CharField(max_length=128, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # Strava Integration Fields
    strava_refresh_token = models.CharField(max_length=255, blank=True, null=True)
    last_sync_timestamp = models.DateTimeField(blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = 'firebase_uid'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name or self.email or self.phone_number or self.firebase_uid
