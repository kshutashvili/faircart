from __future__ import unicode_literals

import random
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
        if 'fail_silently' not in kwargs:
            kwargs['fail_silently'] = not settings.DEBUG
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_sms(self, msg, sender=None):
        send_sms(msg, self.phone, sender=sender)

    def is_contact_verified(self, ctype):
        if ctype not in ContactVerification.TYPE._ALL:
            msg = 'Unknown contact type: %s; choices are: %s.'
            raise ValueError(msg % (ctype,
                                    ', '.join(ContactVerification.TYPE._ALL)))
        try:
            ContactVerification.objects.verified().get(type=ctype, user=self)
        except ContactVerification.DoesNotExist:
            return False
        return True


class ContactVerificationManager(models.Manager):
    use_for_related_fields = True

    def verifiable(self, *args, **kwargs):
        kwargs['actual_till__gt'] = timezone.now()
        kwargs['verified'] = None
        kwargs['errors__lt'] = settings.CONTACT_VERIF_TRIES
        return self.filter(*args, **kwargs)

    def verified(self, *args, **kwargs):
        return self.exclude(verified=None).filter(*args, **kwargs)


class ContactVerification(models.Model):
    ACTUAL_PERIOD = settings.CONTACT_CODE_ACTUAL

    class Meta:
        verbose_name = _('Verification code')
        verbose_name_plural = _('Verification codes')
        ordering = ('-when_created',)

    class TYPE:
        EMAIL = 'email'
        PHONE = 'phone'
        _CHOICES = ((EMAIL, _('Email')),
                    (PHONE, _('Phone')))
        _LENGTH = {EMAIL: 96,
                   PHONE: 6}
        _ALL = (EMAIL, PHONE)

    MIN_CODE_LEN = min(TYPE._LENGTH.itervalues())
    MAX_CODE_LEN = max(TYPE._LENGTH.itervalues())

    @classmethod
    def get_actual_till(cls):
        return timezone.now() + timedelta(seconds=cls.ACTUAL_PERIOD)

    def __init__(self, *args, **kwargs):
        super(ContactVerification, self).__init__(*args, **kwargs)
        if not self.code:
            self.code = self.generate_code()
        if not self.actual_till:
            self.actual_till = self.get_actual_till()

    def __unicode__(self):
        return '%s: %sverified' % (self.get_contact(),
                                   '' if self.is_verified() else 'not ')

    objects = ContactVerificationManager()

    when_created = models.DateTimeField(_('When created'), auto_now_add=True)
    user = models.ForeignKey(User, related_name='contact_verifications',
                             verbose_name=_('User'))
    code = models.CharField(_('Code'), max_length=MAX_CODE_LEN)
    actual_till = models.DateTimeField(_('Actual till'))
    verified = models.DateTimeField(_('When verified'), blank=True, null=True)
    type = models.CharField(_('Type'), max_length=10, choices=TYPE._CHOICES,
                            default=TYPE.PHONE)
    errors = models.PositiveIntegerField(_('Errors'), default=0, blank=True)

    def get_max_length(self):
        return self.TYPE._LENGTH[self.type]

    def generate_code(self):
        if self.type == self.TYPE.PHONE:
            length = self.get_max_length()
            min_ = 10 ** (length - 1)
            max_ = min_ * 10
            return str(random.randint(min_, max_))
        return get_random_hash()

    def tries_left(self):
        return max(0, settings.CONTACT_VERIF_TRIES - self.errors)

    def is_verified(self):
        return bool(self.verified)

    def is_actual(self):
        return self.actual_till > timezone.now()

    def is_verifiable(self):
        return self.is_actual() and bool(self.tries_left())

    def set_verified(self):
        self.verified = timezone.now()

    def notify(self):
        if self.type == self.TYPE.PHONE:
            self.user.send_sms(_('Your verification code is %s') % self.code)
        elif self.type == self.TYPE.EMAIL:
            message = render_to_string('users/_verify_email_msg.html',
                                       context={'object': self,
                                                'site_url': settings.SITE_URL})
            self.user.email_user(_('Email verification'), message)
        return False

    def get_contact(self):
        return getattr(self.user, self.type)


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    verifications = []
    for ctype in ContactVerification.TYPE._ALL:
        if getattr(instance, ctype, None):
            verifications.append(ContactVerification(user=instance,
                                                     type=ctype))
    ContactVerification.objects.bulk_create(verifications)
    for ver in verifications:
        ver.notify()


@receiver(post_save, sender=ContactVerification)
def on_contact_verification_created(sender, instance, created, **kwargs):
    if created:
        instance.notify()
