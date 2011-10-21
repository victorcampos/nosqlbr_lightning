from django.conf.urls.defaults import patterns, include, url

from webanalytics.webapp.views import home, content, log, metrics, asynchronous_metrics

urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^metrics/?$', metrics, name='metrics'),
    url(r'^metrics/get/?$', asynchronous_metrics, name='metrics'),
    url(r'^content/(?P<page>[0-9])', content, name='content'),
    url(r'^log/(?P<id>[0-9])/(?P<action>[a-z]+)', log, name='log'),
)
