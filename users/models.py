from __future__ import unicode_literals
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core import validators
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin,
                                        BaseUserManager)

from main.utils import get_random_hash
from sms.utils import send_sms


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
                    validators=[validators.RegexValidator(r'^\+\d{9,15}$')])
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

    def send_sms(self, msg, sender=None):
        send_sms(msg, self.phone, sender=sender)


class EmailVerificationManager(models.Manager):
    use_for_related_fields = True

    def verifiable(self, *args, **kwargs):
        kwargs['actual_till__gt'] = timezone.now()
        kwargs['verified'] = None
        return self.filter(*args, **kwargs)


class EmailVerification(models.Model):
    CODE_LEN = 96

    class Meta:
        verbose_name = _('Email verification code')
        verbose_name_plural = _('Email verification codes')
        ordering = ('-when_created',)

    def __unicode__(self):
        return '%s: %sverified' % (self.user.email,
                                   '' if self.is_verified() else 'not ')

    objects = EmailVerificationManager()

    when_created = models.DateTimeField(_('When created'), auto_now_add=True)
    user = models.ForeignKey(User, related_name='email_verifications',
                             verbose_name=_('User'))
    code = models.CharField(_('Code'), max_length=CODE_LEN,
                            default=get_random_hash)
    actual_till = models.DateTimeField(_('Actual till'),
                    default=lambda: timezone.now() + timedelta(seconds=3600))
    verified = models.DateTimeField(_('When verified'), blank=True, null=True)

    def is_verified(self):
        return bool(self.verified)

    def is_actual(self):
        return self.actual_till > timezone.now()

    def set_verified(self):
        self.verified = timezone.now()


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    EmailVerification.objects.create(user=instance)


@receiver(post_save, sender=EmailVerification)
def on_email_verification_created(sender, instance, created, **kwargs):
    message = render_to_string('users/_verify_email_msg.html',
                               context={'object': instance,
                                        'site_url': settings.SITE_URL})
    instance.user.email_user(_('Email verification'), message)
