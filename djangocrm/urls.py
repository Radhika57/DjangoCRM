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
    
    # Carrier
    path('carriers/', views.carrier_list, name='carrier_list'),  
    path('save_carrier/', views.save_carrier, name='save_carrier'),
    path('carriers/detail/<int:carrier_id>/', views.carrier_detail, name='carrier_detail'),
    path('carrier/<int:carrier_id>/delete/', views.delete_carrier, name='delete_carrier'),
    
    
    # Agency
    path('agency/manage-agencies/', views.manage_agencies, name='manage_agencies'),
    path('save-agency/', views.save_agency, name='save_agency'),
    path('agency/<int:agency_id>/edit-details/', views.edit_agency_details, name='edit_agency_details'),
    path('agency/<int:agency_id>/delete/', views.delete_agency, name='delete_agency'),
    
    
    
    # Agents
    path('search-agents/', views.search_agents, name='search_agents'),
    path('save-agent/', views.save_agent, name='save_agent'),
    path('agency/advanced-search/', views.advanced_search, name='advanced_search'),
    path('agency/saved-searches/', views.saved_searches, name='saved_searches'),
    path('agency/detail/<int:agent_id>/', views.agent_detail, name='agent_detail'),
    path('agents/edit/', views.edit_agent, name='edit_agent'),
    path('agent/<int:agent_id>/delete/', views.delete_agent, name='delete_agent'),
    

    # Individual
    
    path('Individuals/search-individuals/', views.search_individuals_list, name='search_individuals_list'),
    path('Individuals/advanced-individuals/', views.advanced_individuals, name='advanced_individuals'),
    path('Individuals/saved-individuals/', views.saved_individuals, name='saved_individuals'),
    path('individuals/create/', views.create_individual, name='create_individual'),
    path('agents/search/', views.agent_autocomplete, name='agent_autocomplete'),
    path('search-carriers/', views.search_carriers, name='search_carriers'),
    path('Individuals/detail/<int:individual_id>/', views.individual_tab, name='individual_tab'),
    path('individuals/search/relationship/', views.search_relationshipindividuals, name='search_relationshipindividuals'),
    path('individuals/create/relationship/', views.create_relationshipindividual, name='create_relationshipindividual'),
    path('individuals/save/basicinfo/', views.save_basic_info, name='save_basic_info'),
    path('individual/<int:individual_id>/delete/', views.delete_individual, name='delete_individual'),
    
    # Policy
    
    path('policy/detail/<int:policy_id>/', views.policy_tab, name='policy_tab'),
    path('policy/search-policy/', views.search_policy, name='search_policy'),
    path('policy/advanced-policy/', views.advanced_policy, name='advanced_policy'),
    path('policy/saved-policy/', views.saved_policy, name='saved_policy'),
    path('save_policy/', views.save_policy, name='save_policy'),
    path('update-policy/', views.update_policy, name='update_policy'),
    path('add-carrier-product/', views.add_carrier_product, name='add_carrier_product'),
    path('policy/<int:policy_id>/delete/', views.delete_policy, name='delete_policy'),
    
    # Prescription
    
    path('prescription/', views.prescription_form, name='prescription_form'),
    path('prescription-table/', views.prescription_table, name='prescription_table'),
    path('get-prescription-data/', views.get_prescription_data, name='get_prescription_data'),
    path('query-drug/', views.query_drug, name='query_drug'),
    path('get-dosage-options/', views.get_dosage_options, name='get_dosage_options'),
    path('save-prescription/', views.save_prescription, name='save_prescription'),
    path('delete-prescription/<int:pk>/', views.delete_prescription, name='delete_prescription'),
    
    
    path('customfields/', views.custom_fields, name='custom_fields'),
    path('agents/settings/', views.agent_column_settings, name='agent_column_settings'),
    
    
  
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
