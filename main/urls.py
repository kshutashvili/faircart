from django.conf.urls import url, patterns


urlpatterns = patterns('main.views',
    url(r'^$', 'landing'),
)
