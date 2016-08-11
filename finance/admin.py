from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from users.admin import HasValueFilter
from finance.models import Wallet, Order, Change, Currency


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
admin.site.register(Currency, CurrencyAdmin)


class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'balance', 'when_created')
    list_filter = ('currency',)
admin.site.register(Wallet, WalletAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'when_created', 'wallet', 'to_user', 'amount')
admin.site.register(Order, OrderAdmin)


class ProcessedFilter(HasValueFilter):
    title = _('Is processed')
    parameter_name = 'processed'
    lookup_pos_name = _('Processed')
    lookup_neg_name = _('Not processed')
    field_name = 'when_processed'


class ChangeAdmin(admin.ModelAdmin):
    list_display = ('when_created', 'wallet', 'amount', 'order')
    list_filter = [ProcessedFilter]
admin.site.register(Change, ChangeAdmin)
