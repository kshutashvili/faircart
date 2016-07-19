from django.conf.urls import url
from django.contrib.auth import views as auth_views

from users.views import RegView, VerifyContactView
from users.models import ContactVerification


urlpatterns = [
    url(r'^login/$', auth_views.login, name='login',
        kwargs={'template_name': 'users/login.html'}),
    url(r'^logout/$', auth_views.logout, name='logout',
        kwargs={'next_page': '/'}),
    url(r'^create/$', RegView.as_view(), name='registration'),
    url(r'^verify/(?P<ctype>(%s))/$' % '|'.join(ContactVerification.TYPE._ALL),
        VerifyContactView.as_view(), name='verify_contact')
]
