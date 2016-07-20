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
        VerifyContactView.as_view(), name='verify_contact'),
    url(r'^password/change/$', auth_views.password_change,
        kwargs={'template_name': 'users/password_change.html'},
        name='password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done,
        kwargs={'template_name': 'users/password_change_done.html'},
        name='password_change_done'),
    url(r'^password/reset/$', auth_views.password_reset,
        kwargs={'template_name': 'users/password_reset_form.html',
                'email_template_name': 'users/_email_reset_pass.html',
                'subject_template_name': 'users/_email_reset_pass_subj.txt'},
        name='password_reset_request'),
    url(r'^password/reset/sent/$', auth_views.password_reset_done,
        kwargs={'template_name': 'users/password_reset_sent.html'},
        name='password_reset_done'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, name='password_reset_confirm',
        kwargs={'template_name': 'users/password_reset_confirm.html'},),
    url(r'^password/reset/done/$', auth_views.password_reset_complete,
        kwargs={'template_name': 'users/password_reset_done.html'},
        name='password_reset_complete'),
]
