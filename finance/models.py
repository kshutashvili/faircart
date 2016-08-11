from __future__ import unicode_literals
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _


class Currency(models.Model):
    class Meta:
        verbose_name = _('Currency')
        verbose_name_plural = _('Currencies')

    def __unicode__(self):
        return self.code

    code = models.CharField(_('Code'), max_length=10, primary_key=True)
    name = models.CharField(_('Name'), max_length=70)


class Wallet(models.Model):
    class Meta:
        verbose_name = _('Wallet')
        verbose_name_plural = _('Wallets')

    def __unicode__(self):
        return '%i [%s]' % (self.id, self.currency_id)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'),
                             related_name='wallets')
    currency = models.ForeignKey(Currency, verbose_name=_('Currency'),
                                 related_name='wallets')
    balance = models.DecimalField(_('Balance'), default=Decimal(0.0),
                                  max_digits=20, decimal_places=2)
    when_created = models.DateTimeField(_('When created'), auto_now_add=True)


class Order(models.Model):
    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Order')

    def __unicode__(self):
        return '#%i' % self.id

    wallet = models.ForeignKey(Wallet, verbose_name=_('From wallet'),
                               related_name='orders')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL,
                                verbose_name=_('To user'),
                                related_name='income_orders')
    amount = models.DecimalField(_('Amount'), decimal_places=2, max_digits=20,
                                 default=Decimal(0.0))
    when_created = models.DateTimeField(_('When created'), auto_now_add=True)


class Change(models.Model):
    class Meta:
        verbose_name = _('Change')
        verbose_name_plural = _('Changes')
        ordering = ('-when_created',)

    wallet = models.ForeignKey(Wallet, verbose_name=_('Wallet'),
                               related_name='changes')
    amount = models.DecimalField(_('Amount'), decimal_places=2, max_digits=20,
                                 default=Decimal(0.0))
    when_created = models.DateTimeField(_('When created'),
                                        default=timezone.now)
    order = models.ForeignKey(Order, verbose_name=_('Order'),
                              related_name='changes', blank=True, null=True)

    def process(self, save=True):
        self.wallet.balance += self.amount
        if save:
            self.wallet.save()


@receiver(post_save, sender=Order)
def on_order_created(sender, instance, created, **kwargs):
    if not created:
        return
    currency = instance.wallet.currency_id
    try:
        wallet = instance.to_user.wallets.get(currency_id=currency)
    except Wallet.DoesNotExist:
        wallet = Wallet.objects.create(user=instance.to_user,
                                       currency_id=currency)
    Change.objects.create(wallet=instance.wallet,
                          amount=-instance.amount,
                          order=instance)
    Change.objects.create(wallet=wallet,
                          amount=instance.amount,
                          order=instance)


@receiver(post_save, sender=Change)
def on_change_created(sender, instance, created, **kwargs):
    if created:
        instance.process()
