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
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('carriers/', views.carrier_list, name='carrier_list'),  
    path('save_carrier/', views.save_carrier, name='save_carrier'),
    path('carriers/detail/<int:carrier_id>/', views.carrier_detail, name='carrier_detail'),
    path('carriers/address/edit/<int:address_id>/', views.edit_carrier_address, name='edit_carrier_address'),
    path('carrier/address/delete/<int:address_id>/', views.delete_carrier_address, name='delete_carrier_address'),
    path('customfields/', views.custom_fields, name='custom_fields'),
    path('search-agents/', views.search_agents, name='search_agents'),
    path('agents/manage-agencies/', views.manage_agencies, name='manage_agencies'),
    path('agents/settings/', views.agent_column_settings, name='agent_column_settings'),
    path('agency/detail/<int:agency_id>/', views.agency_detail, name='agency_detail'),
    
    path('agentcolumnsettings/', views.agent_column_settings, name='agentcolumnsettings'), 
    path('agency/agency-eo/', views.agency_eo, name='agency_eo'),
    path('agency/advanced-search/', views.advanced_search, name='advanced_search'),
    path('agency/saved-searches/', views.saved_searches, name='saved_searches'),
    path('agency/agency-client/', views.agency_client, name='agency_client'),
   
    path('agency/agency-agency-activity/', views.agency_activity, name='agency_activity'),
    path('agency/agency-agency-note/', views.agency_note, name='agency_note'),
    path('policy/detail/<int:policy_id>/', views.policy_detail, name='policy_detail'),
    path('policy/search-policy/', views.search_policy, name='search_policy'),
    path('policy/advanced-policy/', views.advanced_policy, name='advanced_policy'),
    path('policy/saved-policy/', views.saved_policy, name='saved_policy'),
    path('agency/senior-select/', views.senior_select, name='senior_select'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
