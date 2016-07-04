from django.conf.urls import url

from users.views import RegView


urlpatterns = [
    url(r'^create/$', RegView.as_view(), name='registration'),
]
