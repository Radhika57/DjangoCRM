from django.contrib import admin
from main.models import *


class CarrierAdmin(admin.ModelAdmin):
    model = Carrier
    list_display = ['name']
    
admin.site.register(Carrier,CarrierAdmin)
