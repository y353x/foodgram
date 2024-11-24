from django.urls import path

from shortlink.views import s_link_redirect

urlpatterns = [
    path('<str:short_link>/', s_link_redirect, name='s_link_redirect'),
]
