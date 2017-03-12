from django.conf.urls import include, url
from rest_framework import routers

from tempo.events import views

events = routers.DefaultRouter()
events.register(r'entries', views.EntryViewSet, base_name='entries')
events.register(r'configs', views.ConfigViewSet, base_name='configs')

v1_patterns = [
    url(r'^events/', include(events.urls, namespace='events')),
    url(r'^search$', views.Search.as_view(), name='search'),
]

urlpatterns = [
    url(r'^v1/', include(v1_patterns, namespace='v1')),

]
