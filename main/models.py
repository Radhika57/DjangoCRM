from django.db import models
from multiselectfield import MultiSelectField

CARRIER_SECURITY_GROUP_CHOICES = (
    ('administrator', 'Administrator'),
    ('agent_gem', 'Agent GEM'),
    ('agent_statements', 'Agent Statements'),
    ('commission_staff', 'Commission Staff'),
)

STATE_CHOICES = (
    ('Alabama', 'Alabama'),
    ('Alaska', 'Alaska'),
    ('Arizona', 'Arizona'),
    ('Arkansas', 'Arkansas'),
    
)

CARRIER_STATUS_CHOICES = (
    ('active','Active'),
    ('inactive','InActive')
)

ADDRESS_TYPE_CHOICES = (
    ('Business','Business'),
    ('Home','Home'),
    ('Other','Other')
)

class Carrier(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CarrierDetails(models.Model):
    carrier = models.OneToOneField(Carrier, on_delete=models.CASCADE, related_name='carrier_details')
    abbreviation = models.CharField(max_length=200,null=True,blank=True)
    security_groups = MultiSelectField(choices=CARRIER_SECURITY_GROUP_CHOICES, null=True,blank=True)
    carrier_status = models.CharField(max_length=100,choices=CARRIER_STATUS_CHOICES,null=True,blank=True)
    

class CarrierPhone(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='phones')
    phone_type = models.CharField(max_length=50, blank=True, null=True)  
    number = models.CharField(max_length=20, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)

class CarrierAddress(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=50, choices=ADDRESS_TYPE_CHOICES,blank=True, null=True)  
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    primary = models.BooleanField(default=False)


class CarrierActivity(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE , related_name='carrieractivity')
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    follow_up_user = models.CharField(max_length=100)
    follow_up_team = models.CharField(max_length=100)
    due_date = models.DateField(null=True, blank=True)
    activity_date = models.DateField()
    priority = models.CharField(max_length=50)
    activity_type = models.CharField(max_length=50)
    method = models.CharField(max_length=50)
    attachment = models.FileField(upload_to='carrier_activity_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CarrierNotes(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE , related_name='carriernotes')
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='carrier_notes_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class CarrierFormName(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE , related_name='carrierformname')
    form_name = models.CharField(max_length=100,blank=True)
    year = models.CharField(max_length=100,blank=True)
    form_number = models.CharField(max_length=100,blank=True)
    coverage_type = models.CharField(max_length=100,blank=True)
    form_file = models.FileField(upload_to='carrier_notes_attachments/', null=True, blank=True)
    
class CarrierProduct(models.Model):
    COVERAGE_CHOICES = [
        ('Medical', 'Medical'),
        ('Dental', 'Dental'),
        ('Vision', 'Vision'),
    ]

    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='products')
    coverage_type = models.CharField(max_length=50, choices=COVERAGE_CHOICES)
    product_name = models.CharField(max_length=255)
    effective_date = models.DateField(null=True, blank=True)
    term_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    benefit_summary = models.FileField(upload_to='product_files/', null=True, blank=True)
    plan_grid = models.FileField(upload_to='product_files/', null=True, blank=True)
    brochure = models.FileField(upload_to='product_files/', null=True, blank=True)

    states = MultiSelectField(choices=STATE_CHOICES, null=True,blank=True)  
    # modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_name} ({self.coverage_type})"
    
    
class CarrierWebsite(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE,related_name="websites")
    website_name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.carrier.name} - {self.website_name}"