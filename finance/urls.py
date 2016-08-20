from django.conf.urls import url

from finance.views import TransferView


urlpatterns = [
    url(r'^transfer/$', TransferView.as_view(), name='transfer')
]
