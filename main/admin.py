from django.contrib import admin
from main.models import *


class CarrierAdmin(admin.ModelAdmin):
    model = Carrier
    list_display = ['name']
    
class CarrierDetailsAdmin(admin.ModelAdmin):
    model = CarrierDetails
    list_display = ['carrier','abbreviation','security_groups','carrier_status']
    
class CarrierPhoneAdmin(admin.ModelAdmin):
    model = CarrierPhone
    list_display = ['carrier','phone_type','number','extension']
    
class CarrierAddressAdmin(admin.ModelAdmin):
    model = CarrierAddress
    list_display = ['carrier','address_type','primary','address1','address2','city','state','zip_code','county','description']
    
class CarrierActivityAdmin(admin.ModelAdmin):
    model = CarrierActivity
    list_display = ['carrier','subject','notes','status','follow_up_user','follow_up_team','due_date','activity_date','priority','activity_type','method','attachment']
    
class CarrierNotesAdmin(admin.ModelAdmin):
    model = CarrierNotes
    list_display = ['carrier','subject','notes','attachment']
    
class CarrierFormsAdmin(admin.ModelAdmin):
    model = CarrierFormName
    list_display = ['carrier','form_name','year','form_number','coverage_type','form_file']
    
admin.site.register(Carrier,CarrierAdmin)
admin.site.register(CarrierDetails,CarrierDetailsAdmin)
admin.site.register(CarrierPhone,CarrierPhoneAdmin)
admin.site.register(CarrierAddress,CarrierAddressAdmin)
admin.site.register(CarrierActivity,CarrierActivityAdmin)
admin.site.register(CarrierNotes,CarrierNotesAdmin)
admin.site.register(CarrierFormName,CarrierFormsAdmin)
admin.site.register(CarrierProduct)
admin.site.register(CarrierWebsite)
admin.site.register(Agency)
admin.site.register(AgencyDetails)
admin.site.register(AgencyAddress)
admin.site.register(AgencyPhone)
admin.site.register(AgencyNotes)
admin.site.register(Agent)
admin.site.register(Agent_Activity)
admin.site.register(Agent_details)
admin.site.register(Agent_EO)
admin.site.register(Agent_license)
admin.site.register(Agent_personal)
admin.site.register(AgentNotes)
admin.site.register(Agents_contract)
admin.site.register(AgentPhone)
admin.site.register(AgentAddress)
admin.site.register(AgentAgencies)
admin.site.register(Individuals)
admin.site.register(IndividualDetails)
admin.site.register(IndividualAddress)
admin.site.register(IndividualActivity)
admin.site.register(IndividualNotes)
admin.site.register(IndividualRelationship)
