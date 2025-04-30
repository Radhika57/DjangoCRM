"""
URL configuration for djangocrm project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from django.conf.urls.static import static # type: ignore # type: ignore
from django.conf import settings # type: ignore
from main import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),  # Main dashboard view
    path('carriers/', views.carrier_list, name='carrier_list'),  # List of carriers
    path('carriers/detail/', views.carrier_detail, name='carrier_detail'),
    path('carriers/individuals/', views.individuals_view, name='individuals'),
     path('customfields/', views.custom_fields, name='custom_fields'),

    
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

