"""
URL configuration for ecobudget project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tracker.views import home_page, login_page, register_page, dashboard_page, logout_view

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('dashboard/', dashboard_page, name='dashboard_page'),
    path('logout/', logout_view, name='logout_page'),
    path('admin/', admin.site.urls),
    path('api/', include('tracker.urls')),
]
