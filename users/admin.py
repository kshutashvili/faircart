from django.contrib import admin
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, ContactVerification
from users.forms import UserCreationForm, UserChangeForm


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2'),
        }),
    )

    list_display = ('phone', 'email', 'first_name', 'last_name', 'is_staff',
                    'is_superuser', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('phone', 'email')
    ordering = ('-date_joined',)
admin.site.register(User, UserAdmin)


def boolfunc(funcname, descr=None):
    def inner(self, obj, funcname=funcname):
        return getattr(obj, funcname)()

    if descr is None:
        descr = funcname.replace('_', ' ').capitalize()
    inner.short_description = descr
    inner.boolean = True
    return inner


class ActualFilter(admin.SimpleListFilter):
    title = _('Is actual')
    parameter_name = 'actual'

    def lookups(self, request, model_admin):
        return ((1, 'Actual'),
                (0, 'Not actual'))

    def queryset(self, request, queryset):
        value = self.value()
        try:
            value = int(value)
        except (ValueError, TypeError):
            return queryset
        if value == 0:
            return queryset.filter(actual_till__lte=timezone.now())
        else:
            return queryset.filter(actual_till__gt=timezone.now())


class VerifiedFilter(admin.SimpleListFilter):
    title = _('Is verified')
    parameter_name = 'verified'

    def lookups(self, request, model_admin):
        return ((1, 'Verified'),
                (0, 'Not verified'))

    def queryset(self, request, queryset):
        value = self.value()
        try:
            value = int(value)
        except (ValueError, TypeError):
            return queryset
        func = queryset.filter if value == 0 else queryset.exclude
        return func(verified=None)


class ContactVerificationAdmin(admin.ModelAdmin):
    list_display = ('when_created', 'user', 'actual_till', 'is_actual',
                    'is_verified')
    list_filter = [ActualFilter, VerifiedFilter]

    is_verified = boolfunc('is_verified')
    is_actual = boolfunc('is_actual')
admin.site.register(ContactVerification, ContactVerificationAdmin)