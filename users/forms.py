from django import forms
from django.contrib.auth.forms import (UserCreationForm as BaseUCrForm,
                                       UserChangeForm as BaseUChForm)
from users.models import User


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
