from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from users.views import RegView


urlpatterns = [
    url(r'^login/$', auth_views.login, name='login',
        kwargs={'template_name': 'users/login.html'}),
    url(r'^logout/$', auth_views.logout, name='logout',
        kwargs={'next_page': '/'}),
    url(r'^create/$', RegView.as_view(), name='registration'),
]
