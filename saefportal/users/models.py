from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, is_active, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          is_active=is_active,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          last_login=now,
                          date_joined=now,
                          **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self._create_user(email, password, False, False, False, **extra_fields)
        return user

    def create_superuser(self, email, password, **extra_fields):
        user = self._create_user(email, password, True, True, True, **extra_fields)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True, db_index=True, verbose_name=_('email address'))
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    firstname = models.CharField(max_length=32, default='')
    lastname = models.CharField(max_length=32, default='')
    organization = models.CharField(max_length=32, default='')
    phone = models.CharField(max_length=20, default='')

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
