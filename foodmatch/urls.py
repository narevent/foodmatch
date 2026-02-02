# main_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from dating.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', lambda request: redirect('dating:discover')),
    path('', login_view),
    path('dating/', include('dating.urls')),
]