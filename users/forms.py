from django import forms
from django.contrib.auth.forms import (UserCreationForm as BaseUCrForm,
                                       UserChangeForm as BaseUChForm)
from django.utils.translation import ugettext_lazy as _
from users.models import User, ContactVerification


class UserCreationForm(BaseUCrForm):
    class Meta:
        model = User
        fields = [User.USERNAME_FIELD]


class UserChangeForm(BaseUChForm):
    class Meta:
        model = User
        fields = '__all__'


class RegForm(UserCreationForm):
    accept_rules = forms.BooleanField(initial=False, required=True)

    class Meta(UserCreationForm.Meta):
        fields = ['phone', 'email']


class ContactVerificationForm(forms.Form):
    code = forms.CharField(min_length=ContactVerification.MIN_CODE_LEN,
                           max_length=ContactVerification.MAX_CODE_LEN,
                           label=_('Code'))
