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
