from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        r'^system_settings$',
        views.SystemSettingsView.as_view(),
        name='system_settings'
    )
]
