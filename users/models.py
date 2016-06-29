from __future__ import unicode_literals

from django.db import models
from django.core import validators
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone, email, password, **extra_fields)

    def create_superuser(self, phone, email, password, **extra_fields):
        for field in ('is_staff', 'is_superuser'):
            extra_fields.setdefault(field, True)
            if extra_fields.get(field) is not True:
                raise ValueError('Superuser must have %s=True.' % field)
        return self._create_user(phone, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        abstract = False

    phone = models.CharField(_('Phone'), max_length=16, unique=True,
                validators=[validators.RegexValidator(regex=r'^\+\d{9,15}$')])
    first_name = models.CharField(_('First name'), max_length=30, blank=True)
    last_name = models.CharField(_('Last name'), max_length=30, blank=True)
    email = models.EmailField(_('Email address'), blank=True)
    is_staff = models.BooleanField(_('Staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'),)
    is_active = models.BooleanField(_('Is active'), default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('When joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email']

    def set_username(self, value):
        setattr(self, self.USERNAME_FIELD, value)

    # username is used for compatibility
    # with built-in creation and change forms
    username = property(AbstractBaseUser.get_username, set_username)

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)
