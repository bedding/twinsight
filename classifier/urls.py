from django.conf.urls import patterns, url

from classifier import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^index$', views.index, name='index'),
    url(r'^(?P<testtweet_id>\d+)/tag/$', views.tag, name='tag'),
    url(r'^test$', views.test, name='test'),
    url(r'^analysis/(?P<keyword>.+)$', views.analysis_keyword, name='analysis_keyword'),
    url(r'^analysis$', views.analysis_keyword, name='analysis_keyword'),
)
