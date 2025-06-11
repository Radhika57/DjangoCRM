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

PRIMARY_MARKET_CHOICES = (
    ('Med Supp', 'Med Supp'),
    ('Health', 'Health'),
    ('Life', 'Life'),
    ('P&C', 'P&C'),
    
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

TEAM_CHOICES = (
    ('Team 1','Team 1'),
    ('Team 2','Team 2'),
    ('Your Sales Pipeline Team','Your Sales Pipeline Team')
)

AGENT_TYPE_CHOICES = (
    ('Active_Contracted','Active_Contracted'),
    ('Onbording','Onbording'),
    ('Prospect','Prospect'),
    ('Termed','Termed'),
    ('Decreased','Decreased'),
    ('Retired','Retired')
)

AGENT_STATUS_CHOICES = (
    ('Completing Paperwork','Completing Paperwork'),
    ('Not Contracted','Not Contracted'),
    ('Not Intrested','Not Intrested'),
    ('Agency Contracted','Agency Contracted'),
    ('Carrier Contracted','Carrier Contracted'),
    ('Contracting W/Carriers','Contracting W/Carriers'),
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
    number = models.CharField(max_length=10, blank=True, null=True)
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
    notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=50,null=True, blank=True)
    follow_up_user = models.CharField(max_length=100,null=True, blank=True)
    follow_up_team = models.CharField(max_length=100,null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    activity_date = models.DateField()
    priority = models.CharField(max_length=50,null=True, blank=True)
    activity_type = models.CharField(max_length=50,null=True, blank=True)
    method = models.CharField(max_length=50,null=True, blank=True)
    attachment = models.FileField(upload_to='carrier_activity_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CarrierNotes(models.Model):
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE , related_name='carriernotes')
    subject = models.CharField(max_length=255)
    pin_note = models.BooleanField(default=False)
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

    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='products')
    coverage_type = models.CharField(max_length=50)
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
    
    
class Agency(models.Model):
    name = models.CharField(max_length=255,unique=True)
    business_phone = models.CharField(max_length=10, blank=True, null=True)
    ext = models.CharField(max_length=12, blank=True, null=True)
    
class AgencyDetails(models.Model):
    agency_name = models.ForeignKey(Agency,on_delete=models.CASCADE,related_name="agency_detail")
    federal_tax_number = models.CharField(max_length=50, blank=True, null=True)
    active = models.BooleanField(default=False)
    email = models.EmailField(null=True,blank=True)
    
class AgencyPhone(models.Model):
    agency_name = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency_phones')
    phone_type = models.CharField(max_length=50, blank=True, null=True)  
    number = models.CharField(max_length=10, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)

class AgencyAddress(models.Model):
    agency_name = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='agency_addresses')
    address_type = models.CharField(max_length=50, choices=ADDRESS_TYPE_CHOICES,blank=True, null=True)  
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    primary = models.BooleanField(default=False)
    
class AgencyNotes(models.Model):
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE , related_name='agencynotes')
    pin_note = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='agency_notes_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
class Agent(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100,null=True,blank=True)
    business_phone = models.CharField(max_length=12,null=True,blank=True)
    ext = models.CharField(max_length=10,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    agent_type = models.CharField(max_length=50,null=True,blank=True)
    status = models.CharField(max_length=50,null=True,blank=True)
    npn = models.CharField(max_length=100,null=True,blank=True)
    agency = models.ForeignKey(Agency,on_delete=models.CASCADE,related_name="agent_agency")
    agent_number = models.CharField(max_length=100,null=True,blank=True)
    
class Agent_details(models.Model):
    agent = models.ForeignKey(Agent,on_delete=models.CASCADE,related_name="agent_detail")
    middle_name = models.CharField(max_length=100,null=True,blank=True)
    nick_name = models.CharField(max_length=100,null=True,blank=True)
    ssn = models.CharField(max_length=100,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    classification = models.CharField(max_length=100,null=True,blank=True)
    secondary_email = models.EmailField(null=True,blank=True)
    lead_date = models.DateField(null=True,blank=True)
    lead_source = models.CharField(max_length=100,null=True,blank=True)
    other_lead_source = models.CharField(max_length=100,null=True,blank=True)
    project_code = models.CharField(max_length=100,null=True,blank=True)
    primary_market = MultiSelectField(choices=PRIMARY_MARKET_CHOICES, null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    team = MultiSelectField(choices=TEAM_CHOICES,null=True,blank=True)
    # representative 
    business_name = models.CharField(max_length=100,null=True,blank=True)
    key_agent = models.BooleanField(default=False)
    
class AgentPhone(models.Model):
    agent_name = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='agent_phones')
    phone_type = models.CharField(max_length=50, blank=True, null=True)  
    number = models.CharField(max_length=10, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)

class AgentAddress(models.Model):
    agent_name = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='agent_addresses')
    address_type = models.CharField(max_length=50, choices=ADDRESS_TYPE_CHOICES,blank=True, null=True)  
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    primary = models.BooleanField(default=False)
    
class AgentAgencies(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_agencies')
    agency = models.ForeignKey(Agency,on_delete=models.SET_NULL,null=True)
    agent_number = models.CharField(max_length=100,null=True,blank=True)
    active = models.BooleanField(default=False)
    
class Agent_Activity(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_activity')
    pin_note = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    # follow_up_user = models.CharField(max_length=100,null=True,blank=True)
    follow_up_team = models.CharField(max_length=100,null=True,blank=True)
    due_date = models.DateField(null=True, blank=True)
    activity_date = models.DateField(null=True,blank=True)
    priority = models.CharField(max_length=100,null=True,blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    method = models.CharField(max_length=100,null=True,blank=True)
    attachment = models.FileField(upload_to='agent_activity_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class AgentNotes(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_notes')
    pin_note = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    notes = models.TextField(null=True,blank=True)
    attachment = models.FileField(upload_to='agent_notes_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Agent_EO(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_eo')
    eo_required = models.BooleanField(default=False)
    eo_expiration_date = models.DateField(null=True,blank=True)
    eo_attachment = models.FileField(upload_to='agent_eo_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Agents_contract(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_contract')
    carrier = models.ForeignKey(Carrier,on_delete=models.SET_NULL,null=True)
    contract_status = models.CharField(max_length=100,null=True,blank=True)
    contact_file = models.FileField(upload_to='agent_contract_file/', null=True, blank=True)
    direct_paid_by_carrier = models.BooleanField(default=False)
    agent_number1 = models.CharField(max_length=100,null=True,blank=True)
    agent_number2 = models.CharField(max_length=100,null=True,blank=True)
    agent_number3 = models.CharField(max_length=100,null=True,blank=True)
    medicare_number = models.CharField(max_length=100,null=True,blank=True)
    contract_date = models.DateField(null=True,blank=True)
    certified_date = models.DateField(null=True,blank=True)
    termination_date = models.DateField(null=True,blank=True)
    termination_reason = models.CharField(max_length=100,null=True,blank=True)
    agent_state = models.CharField(max_length=100,null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    
class Agent_license(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_license')
    license_number = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    resident_state = models.BooleanField(default=False)
    effective_date = models.DateField(null=True,blank=True)
    expiration_date = models.DateField(null=True,blank=True)
    license_file = models.FileField(upload_to='agent_license_file/', null=True, blank=True)
    qualifications = models.CharField(max_length=100,null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    
class Agent_personal(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE , related_name='agent_personal')
    spouse_name = models.CharField(max_length=100,null=True,blank=True)
    anniversary_date = models.DateField(null=True,blank=True)
    children_names = models.TextField(null=True,blank=True)
    incentives = models.TextField(null=True,blank=True)
    hobbies = models.TextField(null=True,blank=True)
    additional_information = models.TextField(null=True,blank=True)
    
class Individuals(models.Model):
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100)
    individual_type = models.CharField(max_length=100,null=True,blank=True)
    servicing_agent = models.ForeignKey(Agent,on_delete=models.CASCADE,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    business_phone = models.CharField(max_length=10, blank=True, null=True)
    business_ext = models.CharField(max_length=10, blank=True, null=True)
    home_phone = models.CharField(max_length=10, blank=True, null=True)
    home_ext = models.CharField(max_length=10, blank=True, null=True)
    cell_phone = models.CharField(max_length=10, blank=True, null=True)
    cell_ext = models.CharField(max_length=10, blank=True, null=True)
    carrier = models.ForeignKey(Carrier,on_delete=models.SET_NULL,null=True,blank=True)

class IndividualDetails(models.Model):
    individual_name = models.ForeignKey(Individuals,on_delete=models.CASCADE,related_name="individual_detail")
    nick_name = models.CharField(max_length=100,null=True,blank=True)
    title = models.CharField(max_length=10,null=True,blank=True)
    gender = models.CharField(max_length=10,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    ssn = models.CharField(max_length=100,null=True,blank=True)
    driver_license = models.CharField(max_length=100,null=True,blank=True)
    descresed_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    mbi = models.CharField(max_length=100,null=True,blank=True)
    medicare_effective_date_A = models.DateField(null=True,blank=True)
    medicare_effective_date_B = models.DateField(null=True,blank=True)
    smoker_status = models.CharField(max_length=100,null=True,blank=True)
    additional_agent = models.ForeignKey(Agent,on_delete=models.CASCADE,null=True,blank=True,related_name="additional_agent")
    secondary_email = models.EmailField(null=True,blank=True)
    lead_date = models.DateField(null=True,blank=True)
    lead_source = models.CharField(max_length=100,null=True,blank=True)
    other_lead_source = models.CharField(max_length=100,null=True,blank=True)
    project_code = models.CharField(max_length=100,null=True,blank=True)
    affiliate_agent = models.ForeignKey(Agent,on_delete=models.CASCADE,null=True,blank=True,related_name="affiliate_agent")


class IndividualAddress(models.Model):
    individual_name = models.ForeignKey(Individuals, on_delete=models.CASCADE, related_name='individual_addresses')
    address_type = models.CharField(max_length=50, choices=ADDRESS_TYPE_CHOICES,blank=True, null=True)  
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    county = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    primary = models.BooleanField(default=False)
    
class IndividualActivity(models.Model):
    individual_name = models.ForeignKey(Individuals, on_delete=models.CASCADE , related_name='individual_activity')
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    # follow_up_user = models.CharField(max_length=100,null=True,blank=True)
    follow_up_team = models.CharField(max_length=100,null=True,blank=True)
    due_date = models.DateField(null=True, blank=True)
    activity_date = models.DateField(null=True,blank=True)
    priority = models.CharField(max_length=100,null=True,blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    method = models.CharField(max_length=100,null=True,blank=True)
    attachment = models.FileField(upload_to='individual_activity_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class IndividualNotes(models.Model):
    individual_name = models.ForeignKey(Individuals, on_delete=models.CASCADE , related_name='individual_notes')
    pin_note = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    notes = models.TextField(null=True,blank=True)
    attachment = models.FileField(upload_to='individual_notes_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class IndividualRelationship(models.Model):
    individual_name = models.ForeignKey(Individuals, on_delete=models.CASCADE , related_name='individual_relationship')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    notes = models.TextField(null=True,blank=True)
    correspondence = models.CharField(max_length=100)
    correspondence_relationship = models.CharField(max_length=100,null=True,blank=True)
    correspondence_notes = models.TextField(null=True,blank=True)
    

class RelationshipBasicInfo(models.Model):
    individual_name = models.ForeignKey(Individuals, on_delete=models.SET_NULL,null=True,blank=True , related_name='individual_relationship_basic_info')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100,null=True,blank=True)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10,null=True,blank=True)
    dob = models.DateField(null=True,blank=True)
    ssn = models.CharField(max_length=100,null=True,blank=True)
    smoker_status = models.CharField(max_length=100,null=True,blank=True)
    
class Policy(models.Model):
    individual = models.ForeignKey(Individuals, on_delete=models.CASCADE, related_name='policy_individual')
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, related_name='policy_carrier')
    policy_number = models.CharField(max_length=100,null=True , blank=True)
    status = models.CharField(max_length=100)
    coverage_type = models.CharField(max_length=100)
    effective_date = models.DateField(null=True,blank=True)
    agent =  models.ForeignKey(Agent,on_delete=models.SET_NULL,null=True,blank=True,related_name="policy_agent")
    
class PolicyDetails(models.Model):
    policy_name = models.ForeignKey(Policy, on_delete=models.CASCADE , related_name='policy_details')
    premium = models.CharField(max_length=20,null=True,blank=True)
    pay_frequency = models.CharField(max_length=100,null=True,blank=True)
    lives = models.CharField(max_length=20,null=True,blank=True)
    project_code = models.CharField(max_length=100,null=True,blank=True)
    app_submit_date = models.DateField(null=True,blank=True)
    renewal_date = models.DateField(null=True,blank=True)
    term_date = models.DateField(null=True,blank=True)
    signed_by =  models.ForeignKey(Agent,on_delete=models.SET_NULL,null=True,blank=True,related_name="signed_by_agent")
    additional_agent =  models.ForeignKey(Agent,on_delete=models.SET_NULL,null=True,blank=True,related_name="policy_additional_agent")
    pay_method = models.CharField(max_length=100,null=True,blank=True)
    notes = models.TextField(null=True,blank=True)
    member_id = models.CharField(max_length=100,null=True,blank=True)
    election = models.CharField(max_length=100,null=True,blank=True)
    who_is_covered = models.BooleanField(default=False)
    election_notes = models.TextField(null=True,blank=True)
    
    
class PolicyActivity(models.Model):
    policy_name = models.ForeignKey(Policy, on_delete=models.CASCADE , related_name='policy_activity')
    subject = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    # follow_up_user = models.CharField(max_length=100,null=True,blank=True)
    follow_up_team = models.CharField(max_length=100,null=True,blank=True)
    due_date = models.DateField(null=True, blank=True)
    activity_date = models.DateField(null=True,blank=True)
    priority = models.CharField(max_length=100,null=True,blank=True)
    type = models.CharField(max_length=100,null=True,blank=True)
    method = models.CharField(max_length=100,null=True,blank=True)
    attachment = models.FileField(upload_to='policy_activity_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class PolicyNotes(models.Model):
    policy_name = models.ForeignKey(Policy, on_delete=models.CASCADE , related_name='policy_notes')
    pin_note = models.BooleanField(default=False)
    subject = models.CharField(max_length=255)
    notes = models.TextField(null=True,blank=True)
    attachment = models.FileField(upload_to='policy_notes_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class PolicyCoverage(models.Model):
    policy_name = models.ForeignKey(Policy, on_delete=models.CASCADE , related_name='policy_coverage')
    carrier_product = models.ForeignKey(CarrierProduct, on_delete=models.SET_NULL, null=True)
    coverage_status = models.CharField(max_length=50, choices=[("Active", "Active"), ("Inactive", "Inactive")], blank=True)
    coverage_effective_date = models.DateField(null=True, blank=True)
    coverage_premium = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    coverage_renewal_date = models.DateField(null=True, blank=True)
    coverage_renewal = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    coverage_lives = models.CharField(max_length=20,null=True, blank=True)
    coverage_termination_policy = models.CharField(max_length=255, blank=True)
    coinsurance = models.CharField(max_length=50, blank=True)
    deductible = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deductible_family = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_out_of_pocket = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_out_of_pocket_family = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    out_of_network_costs = models.TextField(blank=True)
    annual_maximum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    lifetime_maximum = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rx_tier1 = models.CharField(max_length=255, blank=True)
    rx_tier2 = models.CharField(max_length=255, blank=True)
    rx_tier3 = models.CharField(max_length=255, blank=True)
    rx_tier4 = models.CharField(max_length=255, blank=True)
    rx_tier5 = models.CharField(max_length=255, blank=True)
    single_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    plus_spouse_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    plus_children_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    family_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pharmacy_network = models.CharField(max_length=255, blank=True)
    provider_network = models.CharField(max_length=255, blank=True)
    coverage_notes = models.TextField(blank=True)
    fees = models.TextField(blank=True)


class Prescription(models.Model):
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=6)
    refill_frequency = models.CharField(max_length=100)
    generic = models.CharField(max_length=100)