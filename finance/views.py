from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from users.views import VerifiedPhoneRequiredMixin


class TransferView(LoginRequiredMixin,
                   VerifiedPhoneRequiredMixin,
                   TemplateView):
    template_name = 'finance/transfer.html'
