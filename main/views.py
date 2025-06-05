from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse 
from .models import *
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count , Value
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.db.models.functions import Concat
from django.views.decorators.http import require_http_methods , require_POST
import json


def calculate_age(dob):
    if not dob:
        return ''
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def dashboard(request):
    return render(request, "dashboard/index.html")

def clean_phone(number):
    digits = ''.join(filter(str.isdigit, number))  
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return None


def carrier_list(request):
    carriers = Carrier.objects.all()
    return render(request, 'carrier/carrierlist.html', {'carriers': carriers})


def save_carrier(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Carrier.objects.create(name=name)
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Name is required'})


def carrier_detail(request, carrier_id):
    carrier = get_object_or_404(Carrier, id=carrier_id)
    carrier_details = CarrierDetails.objects.filter(carrier=carrier).first()
    carrier_phones = CarrierPhone.objects.filter(carrier=carrier)
    addresses = CarrierAddress.objects.filter(carrier=carrier)
    carrier_forms = CarrierFormName.objects.filter(carrier=carrier)  
    activities = CarrierActivity.objects.filter(carrier=carrier)  
    notess = CarrierNotes.objects.filter(carrier=carrier)  
    products = CarrierProduct.objects.filter(carrier=carrier)
    websites = CarrierWebsite.objects.filter(carrier=carrier)
    individuals = Individuals.objects.filter(carrier=carrier).prefetch_related('individual_detail')

    if request.method == 'POST':

        # --- Carrier Details ---
        if 'abbreviation' in request.POST or 'carrier_status' in request.POST:
            if carrier_details:
                carrier_details.abbreviation = request.POST.get('abbreviation')
                carrier_details.security_groups = request.POST.getlist('security_groups[]')
                carrier_details.carrier_status = request.POST.get('carrier_status')
                carrier_details.save()
            else:
                CarrierDetails.objects.create(
                    carrier=carrier,
                    abbreviation=request.POST.get('abbreviation'),
                    security_groups=request.POST.getlist('security_groups[]'),
                    carrier_status=request.POST.get('carrier_status')
                )

        # --- Phone Numbers ---
        if any(request.POST.get(f"{t}_phone") for t in ['business', 'home', 'cell', 'fax']):
            CarrierPhone.objects.filter(carrier=carrier).delete()
            phone_types = ['business', 'home', 'cell', 'fax']
            for phone_type in phone_types:
                number = request.POST.get(f"{phone_type}_phone")
                extension = request.POST.get(f"{phone_type}_ext")
                if number:
                    formatted = clean_phone(number)
                    if formatted:
                        CarrierPhone.objects.create(
                            carrier=carrier,
                            phone_type=phone_type.capitalize(),
                            number=formatted,
                            extension=extension
                        )

        # --- Address ---
        if request.POST.get('address1') or request.POST.get('address2'):
            address_type = request.POST.get('address_type')
            existing_address = CarrierAddress.objects.filter(carrier=carrier, address_type=address_type).first()
            if existing_address:
                existing_address.address1 = request.POST.get('address1')
                existing_address.address2 = request.POST.get('address2')
                existing_address.zip_code = request.POST.get('zip_code')
                existing_address.city = request.POST.get('city')
                existing_address.state = request.POST.get('state')
                existing_address.description = request.POST.get('description')
                existing_address.primary = request.POST.get('primary_address') == 'on'
                existing_address.save()
            else:
                CarrierAddress.objects.create(
                    carrier=carrier,
                    address_type=address_type,
                    address1=request.POST.get('address1'),
                    address2=request.POST.get('address2'),
                    zip_code=request.POST.get('zip_code'),
                    city=request.POST.get('city'),
                    state=request.POST.get('state'),
                    description=request.POST.get('description'),
                    primary=request.POST.get('primary_address') == 'on'
                )

        # --- Website ---
        if request.POST.get('website_name') and request.POST.get('url'):
            CarrierWebsite.objects.create(
                carrier=carrier,
                website_name=request.POST.get('website_name'),
                url=request.POST.get('url'),
                username=request.POST.get('username'),
                password=request.POST.get('password'),
            )

        # --- Product ---
        if request.POST.get('product_name') and request.POST.get('coverage_type'):
            CarrierProduct.objects.create(
                carrier=carrier,
                coverage_type=request.POST.get('coverage_type'),
                product_name=request.POST.get('product_name'),
                effective_date=request.POST.get('product_effective_date') or None,
                term_date=request.POST.get('product_term_date') or None,
                description=request.POST.get('description'),
                benefit_summary=request.FILES.get('benefit_summary'),
                plan_grid=request.FILES.get('plan_grid'),
                brochure=request.FILES.get('brochure'),
                states=request.POST.getlist('states[]')
            )

        # --- Activity ---
        if request.POST.get('activity_type') and request.POST.get('subject'):
            CarrierActivity.objects.create(
                carrier=carrier,
                subject=request.POST.get('subject'),
                notes=request.POST.get('notes'),
                status=request.POST.get('status'),
                follow_up_user=request.POST.get('follow_up_user'),
                follow_up_team=request.POST.get('follow_up_team'),
                due_date=request.POST.get('due_date') or None,
                activity_date=request.POST.get('activity_date') ,
                priority=request.POST.get('priority'),
                activity_type=request.POST.get('activity_type'),
                method=request.POST.get('method'),
                attachment=request.FILES.get('attachment')
            )

        # --- Notes ---
        if request.POST.get('notes') and request.POST.get('subject'):
            CarrierNotes.objects.create(
                carrier=carrier,
                subject=request.POST.get('subject'),
                notes=request.POST.get('notes'),
                attachment=request.FILES.get('attachment')
            )

        messages.success(request, "Carrier details updated successfully.")
        return redirect('carrier_detail', carrier_id=carrier.id)

    phone_dict = {phone.phone_type.lower(): phone for phone in carrier_phones}
    primary_address = addresses.filter(primary=True).first()

    return render(request, 'carrier/carrierdetail.html', {
        'carrier': carrier,
        'carrier_details': carrier_details,
        'phone_dict': phone_dict,
        'primary_address': primary_address,
        'carrier_forms': carrier_forms,  
        'carrier_phones': carrier_phones,
        'addresses': addresses,
        'activities':activities,
        'notess':notess,
        'products': products,
        'websites': websites,
        'individuals': individuals,
    })


def delete_carrier(request, carrier_id):
    carrier = get_object_or_404(Carrier, id=carrier_id)
    carrier.delete()
    return redirect('carrier_list') 

# Agency

def manage_agencies(request):
    agency = Agency.objects.annotate(agent_count=Count('agent_agency'))
    return render(request, 'agency/manageagencies.html',{'agency': agency})

def save_agency(request):
    if request.method == 'POST':
        name = request.POST.get('agency_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        ext = request.POST.get('ext', '').strip()

        if not name:
            messages.error(request, "Agency name is required.")
            return redirect('manage_agencies')

        try:
            Agency.objects.create(
                name=name,
                business_phone=phone or None,
                ext=ext or None
            )
            messages.success(request, "Agency saved successfully.")
        except IntegrityError:
            messages.warning(request, "An agency with this name already exists.")
        except Exception as e:
            messages.warning(request, f"An error occurred: {str(e)}")

        return redirect('manage_agencies')
    return redirect('manage_agencies')


def edit_agency_details(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)
    agency_details, _ = AgencyDetails.objects.get_or_create(agency_name=agency)
    agency_phones = AgencyPhone.objects.filter(agency_name=agency)
    agency_address = AgencyAddress.objects.filter(agency_name=agency)
    notes = agency.agencynotes.all()

    if request.method == 'POST':

        # --- Agency Details ---
        if 'federal_tax_number' in request.POST or 'email' in request.POST:
            agency_details.federal_tax_number = request.POST.get('federal_tax_number')
            agency_details.email = request.POST.get('email')
            agency_details.active = request.POST.get('active') == 'on'
            agency_details.save()

        # --- Phone Numbers ---
        if any(request.POST.get(f"{t}_phone") for t in ['business', 'home', 'cell', 'fax']):
            AgencyPhone.objects.filter(agency_name=agency).delete()
            phone_types = ['business', 'home', 'cell', 'fax']

            for phone_type in phone_types:
                number = request.POST.get(f"{phone_type}_phone")
                extension = request.POST.get(f"{phone_type}_ext")

                if number:
                    formatted = clean_phone(number)
                    if formatted:
                        AgencyPhone.objects.create(
                            agency_name=agency,
                            phone_type=phone_type.capitalize(),
                            number=formatted,
                            extension=extension
                        )
                    else:
                        print(f"Invalid {phone_type} number: {number}")

        # --- Address ---
        if request.POST.get('address1') or request.POST.get('address2'):
            address_type = request.POST.get('address_type')
            existing_address = AgencyAddress.objects.filter(agency_name=agency, address_type=address_type).first()

            if existing_address:
                existing_address.address1 = request.POST.get('address1')
                existing_address.address2 = request.POST.get('address2')
                existing_address.zip_code = request.POST.get('zip_code')
                existing_address.city = request.POST.get('city')
                existing_address.state = request.POST.get('state')
                existing_address.description = request.POST.get('description')
                existing_address.primary = request.POST.get('primary_address') == 'on'
                existing_address.save()
            else:
                AgencyAddress.objects.create(
                    agency_name=agency,
                    address_type=address_type,
                    address1=request.POST.get('address1'),
                    address2=request.POST.get('address2'),
                    zip_code=request.POST.get('zip_code'),
                    city=request.POST.get('city'),
                    state=request.POST.get('state'),
                    description=request.POST.get('description'),
                    primary=request.POST.get('primary_address') == 'on'
                )

        # --- Notes ---
        if request.POST.get('subject'):
            AgencyNotes.objects.create(
                agency=agency,
                subject=request.POST.get('subject'),
                pin_note=request.POST.get('pin_note') == 'on',
                notes=request.POST.get('notes'),
                attachment=request.FILES.get('attachment')
            )

        messages.success(request, "Agency information updated successfully.")
        return redirect('edit_agency_details', agency_id=agency.id)

    phone_dict = {phone.phone_type.lower(): phone for phone in agency_phones}
    primary_address = agency_address.filter(primary=True).first()

    return render(request, 'agency/seniorselect.html', {
        'agency': agency,
        'agency_details': agency_details,
        'phone_dict': phone_dict,
        'primary_address': primary_address,
        'notess': notes,
        'agency_phones': agency_phones,
        'agency_address': agency_address,
    })

def delete_agency(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)
    agency.delete()
    return redirect('manage_agencies') 

# Agents

def search_agents(request):
    agencies = Agency.objects.all()
    agents = Agent.objects.all()
    return render(request, 'agent/searchagency.html',{'agencies': agencies, 'agents': agents})


def save_agent(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        business_phone = request.POST.get('business_phone', '').strip()
        ext = request.POST.get('extension', '').strip()
        email = request.POST.get('email', '').strip()
        agent_type = request.POST.get('agent_type', '').strip()
        status = request.POST.get('status', '').strip()
        npn = request.POST.get('npn', '').strip()
        agency_id = request.POST.get('agency')
        agent_number = request.POST.get('agent_number', '').strip()

        if not first_name or not last_name or not agency_id:
            messages.error(request, "First Name, Last Name, and Agency are required.")
            return redirect('search_agents')  
        try:
            agency = Agency.objects.get(id=agency_id)
            Agent.objects.create(
                first_name=first_name,
                last_name=last_name,
                business_phone=business_phone or None,
                ext=ext or None,
                email=email or None,
                agent_type=agent_type or None,
                status=status or None,
                npn=npn or None,
                agency=agency,
                agent_number=agent_number or None
            )
            messages.success(request, "Agent saved successfully.")
        except Agency.DoesNotExist:
            messages.error(request, "Selected agency does not exist.")
        except IntegrityError:
            messages.warning(request, "An agent with similar details might already exist.")
        except Exception as e:
            messages.warning(request, f"An error occurred: {str(e)}")

        return redirect('search_agents')
    return redirect('search_agents')

def advanced_search(request):
    return render(request, 'agent/advancedsearch.html')

def saved_searches(request):
    agencies = Agency.objects.all()
    agents = Agent.objects.all()
    return render(request, 'agent/savedsearch.html',{'agencies': agencies, 'agents': agents})


def agent_detail(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    agent_details, _ = Agent_details.objects.get_or_create(agent=agent)
    agent_phones = AgentPhone.objects.filter(agent_name=agent)
    agent_address = AgentAddress.objects.filter(agent_name=agent)
    agent_agencies = AgentAgencies.objects.filter(agent=agent)
    activities = Agent_Activity.objects.filter(agent=agent)
    notes = AgentNotes.objects.filter(agent=agent)
    contract = Agents_contract.objects.filter(agent=agent)
    license = Agent_license.objects.filter(agent=agent)
    agent_eo, _ = Agent_EO.objects.get_or_create(agent=agent)
    agent_personal, _ = Agent_personal.objects.get_or_create(agent=agent)
    agencies = Agency.objects.all()
    carriers = Carrier.objects.all()
    servicing_individuals = Individuals.objects.filter(servicing_agent=agent).prefetch_related('individual_detail')
    policies = Policy.objects.filter(agent=agent).prefetch_related(
    'policy_coverage__carrier_product',
    'policy_details',
    'individual',
    'carrier')

    
    if request.method == 'POST':
        # --- Agent basic info ---
        if 'last_name' in request.POST:
            agent.last_name = request.POST.get('last_name')
            agent.agent_type = request.POST.get('agent_type')
            agent.status = request.POST.get('status')
            agent.npn = request.POST.get('npn')
            agent.email = request.POST.get('email')
            agent.save()

        # --- Agent details ---
        if 'middle_name' in request.POST or 'nick_name' in request.POST:
            agent_details.middle_name = request.POST.get('middle_name')
            agent_details.nick_name = request.POST.get('nick_name')
            agent_details.ssn = request.POST.get('ssn')
            agent_details.date_of_birth = request.POST.get('date_of_birth') or None
            agent_details.classification = request.POST.get('classification')
            agent_details.secondary_email = request.POST.get('secondary_email')
            agent_details.lead_date = request.POST.get('lead_date') or None
            agent_details.lead_source = request.POST.get('lead_source')
            agent_details.other_lead_source = request.POST.get('other_lead_source')
            agent_details.project_code = request.POST.get('project_code')
            agent_details.primary_market = request.POST.getlist('primary_market[]')
            agent_details.notes = request.POST.get('notes')
            agent_details.team = request.POST.getlist('team[]')
            agent_details.business_name = request.POST.get('business_name')
            agent_details.key_agent = request.POST.get('key_agent') == 'on'
            agent_details.save()

        # --- Phones ---
        if any(request.POST.get(f"{t}_phone") for t in ['business', 'home', 'cell', 'fax']):
            AgentPhone.objects.filter(agent_name=agent).delete()
            phone_types = ['business', 'home', 'cell', 'fax']

            for phone_type in phone_types:
                number = request.POST.get(f"{phone_type}_phone")
                extension = request.POST.get(f"{phone_type}_ext")

                if number:
                    formatted = clean_phone(number)
                    if formatted:
                        AgentPhone.objects.create(
                            agent_name=agent,
                            phone_type=phone_type.capitalize(),
                            number=formatted,
                            extension=extension
                        )
                    else:
                        print(f"Invalid {phone_type} number: {number}")

        # --- Address ---
        address_type = request.POST.get('address_type')

        if request.POST.get('address1'):
            existing_address = AgentAddress.objects.filter(agent_name=agent, address_type=address_type).first()

            if existing_address:
                existing_address.address1 = request.POST.get('address1')
                existing_address.address2 = request.POST.get('address2')
                existing_address.zip_code = request.POST.get('zip_code')
                existing_address.city = request.POST.get('city')
                existing_address.state = request.POST.get('state')
                existing_address.description = request.POST.get('description')
                existing_address.primary = request.POST.get('primary_address') == 'on'
                existing_address.save()
            else:
                AgentAddress.objects.create(
                    agent_name=agent,
                    address_type=address_type,
                    address1=request.POST.get('address1'),
                    address2=request.POST.get('address2'),
                    zip_code=request.POST.get('zip_code'),
                    city=request.POST.get('city'),
                    state=request.POST.get('state'),
                    description=request.POST.get('description'),
                    primary=request.POST.get('primary_address') == 'on'
                )



        # --- Agency info ---
        agency_id = request.POST.get('agency')
        if agency_id:
            agency = Agency.objects.filter(id=agency_id).first()
            if agency:
                agent_agency, _ = AgentAgencies.objects.get_or_create(agent=agent, agency=agency)
                agent_agency.agent_number = request.POST.get('agent_number')
                agent_agency.active = request.POST.get('active') == 'on'
                agent_agency.save()

        # --- Activity ---
        if request.POST.get('activity_subject'):
            activity_id = request.POST.get('activity_id')
            if activity_id:
                agent_activity = Agent_Activity.objects.get(id=activity_id)
            else:
                agent_activity = Agent_Activity(agent=agent)

            agent_activity.subject = request.POST.get('activity_subject')
            agent_activity.notes = request.POST.get('activity_notes')
            agent_activity.status = request.POST.get('activity_status')
            agent_activity.follow_up_team = request.POST.get('follow_up_team')
            agent_activity.due_date = request.POST.get('due_date') == 'on'
            agent_activity.activity_date = request.POST.get('activity_date') or None
            agent_activity.priority = request.POST.get('priority')
            agent_activity.type = request.POST.get('type')
            agent_activity.method = request.POST.get('method')
            agent_activity.pin_note = request.POST.get('pin_note') == 'on'
            if request.FILES.get('attachment'):
                agent_activity.attachment = request.FILES.get('attachment')
            agent_activity.save()

        # --- Notes ---
        if request.POST.get('note_subject'):
            note_id = request.POST.get('note_id')
            if note_id:
                agent_note = AgentNotes.objects.get(id=note_id)
            else:
                agent_note = AgentNotes(agent=agent)

            agent_note.subject = request.POST.get('note_subject')
            agent_note.notes = request.POST.get('note_notes')
            agent_note.pin_note = request.POST.get('pin_note') == 'on'
            if request.FILES.get('attachment'):
                agent_note.attachment = request.FILES.get('attachment')
            agent_note.save()

        # --- E&O info ---
        if 'eo_required' in request.POST:
            agent_eo.eo_required = request.POST.get('eo_required') == 'on'
            agent_eo.eo_expiration_date = request.POST.get('eo_expiration_date') or None
            if request.FILES.get('eo_attachment'):
                agent_eo.eo_attachment = request.FILES.get('eo_attachment')
            agent_eo.save()

        # --- Contract ---
        if request.POST.get('carrier'):
            carrier = Carrier.objects.filter(id=request.POST.get('carrier')).first()
            if carrier:
                Agents_contract.objects.create(
                    agent=agent,
                    carrier=carrier,
                    contract_status=request.POST.get('contract_status'),
                    contact_file=request.FILES.get('contact_file'),
                    direct_paid_by_carrier=request.POST.get('direct_paid_by_carrier') == 'on',
                    agent_number1=request.POST.get('agent_number1'),
                    agent_number2=request.POST.get('agent_number2'),
                    agent_number3=request.POST.get('agent_number3'),
                    medicare_number=request.POST.get('medicare_number'),
                    contract_date=request.POST.get('contract_date') or None,
                    certified_date=request.POST.get('certified_date') or None,
                    termination_date=request.POST.get('termination_date') or None,
                    termination_reason=request.POST.get('termination_reason'),
                    agent_state=request.POST.get('agent_state[]'),
                    notes=request.POST.get('contract_notes')
                )
                
        # --- License ---
        if request.POST.get('license_number'):
            Agent_license.objects.create(
                agent=agent,
                license_number=request.POST.get('license_number'),
                state=request.POST.get('state') ,
                resident_state=request.POST.get('resident_state') == 'on',
                effective_date=request.POST.get('effective_date') or None ,
                expiration_date=request.POST.get('expiration_date') or None ,
                license_file=request.FILES.get('license_file'),
                qualifications=request.POST.getlist('qualifications[]') ,
                notes=request.POST.get('license_notes') 
                
            )
                
        # --- Personal ---
            
        if 'spouse_name' in request.POST:
            agent_personal.spouse_name = request.POST.get('spouse_name')
            agent_personal.anniversary_date = request.POST.get('anniversary_date') or None
            agent_personal.children_names = request.POST.get('children_names')
            agent_personal.incentives = request.POST.get('incentives')
            agent_personal.hobbies = request.POST.get('hobbies')
            agent_personal.additional_information = request.POST.get('additional_information')
            agent_personal.save()

        messages.success(request, "Agent details updated successfully.")
        return redirect('agent_detail', agent_id=agent.id)

    phone_dict = {phone.phone_type.lower(): phone for phone in agent_phones}
    primary_address = agent_address.filter(agent_name=agent)

    return render(request, 'agent/agencydetail.html', {
        'agent': agent,
        'agent_details': agent_details,
        'phone_dict': phone_dict,
        'primary_address': primary_address,
        'agent_phones': agent_phones,
        'agent_address': agent_address,
        'agent_agencies': agent_agencies,
        'agencies': agencies,
        'activities': activities,
        'notes': notes,
        'eo': agent_eo,
        'carriers': carriers,
        'contract': contract,
        'agent_personal':agent_personal,
        'license':license,
        'servicing_individuals': servicing_individuals,
        'policies': policies,
    })
    
    
def edit_agent(request):
   return render(request, 'agent/agencyedituser.html')

def delete_agent(request, agent_id):
    agent = get_object_or_404(Agent, id=agent_id)
    agent.delete()
    return redirect('search_agents') 


# Individual


def search_individuals_list(request):
    individual = Individuals.objects.all()
    carriers = Carrier.objects.all()
    context = {
        'individual':individual,
        'carriers':carriers
    }
    return render(request, 'Individuals/searchindividuals.html',context)

def advanced_individuals(request):
    return render(request, 'Individuals/advancedindividuals.html')

def saved_individuals(request):
    return render(request, 'Individuals/savedindividuals.html')

def create_individual(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        individual_type = request.POST.get('type')
        servicing_agent_id = request.POST.get('servicing_agent_id')
        email = request.POST.get('email')
        business_phone = clean_phone(request.POST.get('business_phone'))
        business_ext = request.POST.get('business_ext')
        home_phone = clean_phone(request.POST.get('home_phone'))
        home_ext = request.POST.get('home_ext')
        cell_phone = clean_phone(request.POST.get('cell_phone'))
        cell_ext = request.POST.get('cell_ext')
        record_type = request.POST.get('record_type')
        carrier_name = request.POST.get('carrier_name')

        carrier = None
        if record_type == 'existing':
            carrier = Carrier.objects.filter(name__iexact=carrier_name).first()
        elif record_type == 'new':
            if carrier_name:
                carrier, created = Carrier.objects.get_or_create(name=carrier_name)


        servicing_agent = Agent.objects.filter(id=servicing_agent_id).first() if servicing_agent_id else None

        individual = Individuals.objects.create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            individual_type=individual_type,
            servicing_agent=servicing_agent,
            email=email,
            business_phone=business_phone,
            business_ext=business_ext,
            home_phone=home_phone,
            home_ext=home_ext,
            cell_phone=cell_phone,
            cell_ext=cell_ext,
            carrier=carrier
        )

        return JsonResponse({'success': True, 'message': 'Saved successfully'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def create_relationshipindividual(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        individual_type = request.POST.get('type')
        servicing_agent_id = request.POST.get('servicing_agent_ids')
        email = request.POST.get('email')
        business_phone = clean_phone(request.POST.get('business_phone'))
        business_ext = request.POST.get('business_ext')
        home_phone = clean_phone(request.POST.get('home_phone'))
        home_ext = request.POST.get('home_ext')
        cell_phone = clean_phone(request.POST.get('cell_phone'))
        cell_ext = request.POST.get('cell_ext')
        record_type = request.POST.get('record_type')
        carrier_name = request.POST.get('carrier_name')
        address_ids = request.POST.getlist('address_ids[]') or request.POST.getlist('address_ids')

        carrier = None
        if record_type == 'existing':
            carrier = Carrier.objects.filter(name__iexact=carrier_name).first()
        elif record_type == 'new':
            if carrier_name:
                carrier, created = Carrier.objects.get_or_create(name=carrier_name)

        servicing_agent = Agent.objects.filter(id=servicing_agent_id).first() if servicing_agent_id else None

        individual = Individuals.objects.create(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            individual_type=individual_type,
            servicing_agent=servicing_agent,
            email=email,
            business_phone=business_phone,
            business_ext=business_ext,
            home_phone=home_phone,
            home_ext=home_ext,
            cell_phone=cell_phone,
            cell_ext=cell_ext,
            carrier=carrier
        )
        
        for addr_id in address_ids:
            try:
                
                base_address = IndividualAddress.objects.get(id=addr_id)

        
                IndividualAddress.objects.create(
                    individual_name=individual,  
                    address_type=base_address.address_type,
                    address1=base_address.address1,
                    address2=base_address.address2,
                    city=base_address.city,
                    state=base_address.state,
                    zip_code=base_address.zip_code,
                    description=base_address.description,
                    primary=base_address.primary
                )
            except IndividualAddress.DoesNotExist:
                continue

        return JsonResponse({'success': True,
            'id': individual.id,
            'first_name': individual.first_name,
            'last_name': individual.last_name})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@csrf_exempt
def save_basic_info(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        dob = request.POST.get('dob') or None
        gender = request.POST.get('gender')
        ssn = request.POST.get('ssn')
        smoker_status = request.POST.get('smoker_status')
        individual_id = request.POST.get('individual_id')

        if not first_name or not last_name:
            return JsonResponse({'success': False, 'error': 'First and last name are required'})

        try:
            individual = None
            if individual_id:
                individual = Individuals.objects.get(id=individual_id)

            basic_info = RelationshipBasicInfo.objects.create(
                individual_name=individual,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                dob=dob,
                gender=gender,
                ssn=ssn,
                smoker_status=smoker_status
            )
            return JsonResponse({'success': True, 'id': basic_info.id})

        except Individuals.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Individual not found'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def search_relationshipindividuals(request):
    term = request.GET.get('term', '')
    results = list(Individuals.objects.filter(first_name__icontains=term).values('id', 'first_name', 'last_name')[:10])
    return JsonResponse([{'id': r['id'], 'label': f"{r['first_name']} {r['last_name']}"} for r in results], safe=False)

def search_carriers(request):
    query = request.GET.get('q', '')
    carriers = Carrier.objects.filter(name__icontains=query)[:10]
    data = [{'id': c.id, 'name': c.name} for c in carriers]
    return JsonResponse(data, safe=False)

def agent_autocomplete(request):
    query = request.GET.get('term', '')
    agents = Agent.objects.filter(
        models.Q(first_name__icontains=query) | models.Q(last_name__icontains=query)
    ).values('id', 'first_name', 'last_name')[:10]

    results = [
        {'id': a['id'], 'label': f"{a['first_name']} {a['last_name']}"}
        for a in agents
    ]
    return JsonResponse(results, safe=False)

def get_relationship_data(individual):
    direct_relationships = IndividualRelationship.objects.filter(individual_name=individual)
    basic_infos = RelationshipBasicInfo.objects.filter(individual_name=individual)

    relationship_data = []

    for rel in direct_relationships:
        name_parts = rel.name.strip().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]  
        else:
            first_name = name_parts[0]
            last_name = ''

        
        related_individual = Individuals.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        ).first()

        if related_individual:
            details = IndividualDetails.objects.filter(individual_name=related_individual).first()
            dob = details.dob if details else None

            relationship_data.append({
                'relationship': rel.relationship,
                'name': rel.name,
                'ssn': details.ssn if details else '',
                'dob': dob.strftime('%m/%d/%Y') if dob else '',
                'age': calculate_age(dob),
                'gender': details.gender if details else '',
                'smoker_status': details.smoker_status if details else '',
            })
        else:
            relationship_data.append({
                'relationship': rel.relationship,
                'name': rel.name,
                'ssn': '',
                'dob': '',
                'age': '',
                'gender': '',
                'smoker_status': '',
            })

    
    for rel in basic_infos:
        dob = rel.dob
        full_name = f"{rel.first_name} {rel.middle_name or ''} {rel.last_name}".strip()
        relationship_data.append({
            'relationship': "Basic Info",
            'name': full_name,
            'ssn': rel.ssn or '',
            'dob': dob.strftime('%m/%d/%Y') if dob else '',
            'age': calculate_age(dob),
            'gender': rel.gender or '',
            'smoker_status': rel.smoker_status or '',
        })

    return relationship_data


def individual_tab(request, individual_id):
    individual = get_object_or_404(Individuals,id=individual_id)
    individual_details , _ = IndividualDetails.objects.get_or_create(individual_name=individual)
    individual_address = IndividualAddress.objects.filter(individual_name=individual)
    individual_activity = IndividualActivity.objects.filter(individual_name=individual)
    individual_notes = IndividualNotes.objects.filter(individual_name=individual)
    relationship_data = get_relationship_data(individual)
    policies = Policy.objects.filter(individual=individual).prefetch_related(
    'policy_coverage__carrier_product',
    'policy_details',
    'individual',
    'carrier')
    
    agents = Agent.objects.all()
    if request.method == 'POST':
        if 'last_name' in request.POST:
            individual.middle_name = request.POST.get('middle_name')
            individual.last_name = request.POST.get('last_name')
            individual.individual_type = request.POST.get('type')
            individual.email = request.POST.get('email')
            individual.business_phone = clean_phone(request.POST.get('business_phone'))
            individual.business_ext = request.POST.get('business_ext')
            individual.home_phone = clean_phone(request.POST.get('home_phone'))
            individual.home_ext = request.POST.get('home_ext')
            individual.cell_phone = clean_phone(request.POST.get('cell_phone'))
            individual.cell_ext = request.POST.get('cell_ext')
            servicing_agent_id = request.POST.get('servicing_agent_id')
            if servicing_agent_id:
                individual.servicing_agent = Agent.objects.get(id=servicing_agent_id)

            individual.save()
            
        # --- Individual Details ---
        if 'nick_name' in request.POST or 'title_name' in request.POST:
            individual_details.nick_name = request.POST.get('nick_name')
            individual_details.title = request.POST.get('title_name')
            individual_details.gender = request.POST.get('gender')
            individual_details.dob = request.POST.get('dob') or None
            individual_details.ssn = request.POST.get('ssn')
            individual_details.driver_license = request.POST.get('driver_license')
            individual_details.descresed_date = request.POST.get('deceased_date') or None
            individual_details.status = request.POST.get('status')
            individual_details.mbi = request.POST.get('mbi')
            individual_details.medicare_effective_date_A = request.POST.get('parta') or None
            individual_details.medicare_effective_date_B = request.POST.get('partb') or None
            individual_details.smoker_status = request.POST.get('smoker_status')
            individual_details.secondary_email = request.POST.get('secondary_email')
            individual_details.lead_date = request.POST.get('lead_date') or None
            individual_details.lead_source = request.POST.get('lead_source')
            individual_details.other_lead_source = request.POST.get('other_lead_source')
            individual_details.project_code = request.POST.get('project_code')
            additional_agent_id = request.POST.get('additional_agent_id')
            if additional_agent_id:
                individual_details.additional_agent = Agent.objects.get(id=additional_agent_id)

            affiliate_agent_id = request.POST.get('affiliate_agent_id')
            if affiliate_agent_id:
                individual_details.affiliate_agent = Agent.objects.get(id=affiliate_agent_id)
            individual_details.save()
            
        
        # --- Address ---
        address_type = request.POST.get('address_type')

        if request.POST.get('address1'):
            existing_address = IndividualAddress.objects.filter(individual_name=individual, address_type=address_type).first()

            if existing_address:
                existing_address.address1 = request.POST.get('address1')
                existing_address.address2 = request.POST.get('address2')
                existing_address.zip_code = request.POST.get('zip_code')
                existing_address.city = request.POST.get('city')
                existing_address.state = request.POST.get('state')
                existing_address.description = request.POST.get('description')
                existing_address.primary = request.POST.get('primary_address') == 'on'
                existing_address.save()
            else:
                IndividualAddress.objects.create(
                    individual_name=individual,
                    address_type=address_type,
                    address1=request.POST.get('address1'),
                    address2=request.POST.get('address2'),
                    zip_code=request.POST.get('zip_code'),
                    city=request.POST.get('city'),
                    state=request.POST.get('state'),
                    description=request.POST.get('description'),
                    primary=request.POST.get('primary_address') == 'on'
                )
                
        # --- Activity ---
        if request.POST.get('activity_subject'):
            activity_id = request.POST.get('activity_id')
            if activity_id:
                individual_activity = IndividualActivity.objects.get(id=activity_id)
            else:
                individual_activity = IndividualActivity(individual_name=individual)

            individual_activity.subject = request.POST.get('activity_subject')
            individual_activity.notes = request.POST.get('activity_notes')
            individual_activity.status = request.POST.get('activity_status')
            individual_activity.follow_up_team = request.POST.get('follow_up_team')
            individual_activity.due_date = request.POST.get('due_date') == 'on'
            individual_activity.activity_date = request.POST.get('activity_date') or None
            individual_activity.priority = request.POST.get('priority')
            individual_activity.type = request.POST.get('type')
            individual_activity.method = request.POST.get('method')
            if request.FILES.get('attachment'):
                individual_activity.attachment = request.FILES.get('attachment')
            individual_activity.save()

        # --- Notes ---
        if request.POST.get('note_subject'):
            note_id = request.POST.get('note_id')
            if note_id:
                individual_note = IndividualNotes.objects.get(id=note_id)
            else:
                individual_note = IndividualNotes(individual_name=individual)

            individual_note.subject = request.POST.get('note_subject')
            individual_note.notes = request.POST.get('note_notes')
            individual_note.pin_note = request.POST.get('pin_note') == 'on'
            if request.FILES.get('attachment'):
                individual_note.attachment = request.FILES.get('attachment')
            individual_note.save()
            
        
                # --- Relationship ---
        if 'relation_name' in request.POST and request.POST.get('relation_name').strip():
            relationship_name = request.POST.get('relation_name')
            relationship_to = request.POST.get('relationship')
            relation_notes = request.POST.get('relation_notes')
            correspondence = request.POST.get('corresponding') or ''
            corresponding_relationship = request.POST.get('corresponding_relationship')
            corresponding_notes = request.POST.get('corresponding_notes')

           

            
            IndividualRelationship.objects.create(
                individual_name=individual,
                name=relationship_name,
                relationship=relationship_to,
                notes=relation_notes,
                correspondence=correspondence,
                correspondence_relationship=corresponding_relationship,
                correspondence_notes=corresponding_notes,
            )

        return redirect('individual_tab', individual_id=individual.id)
    
    return render(request, 'Individuals/individualtab.html', {
        'individual': individual,
        'individual_details': individual_details,
        'agents': agents,
        'individual_address': individual_address,
        'individual_activity': individual_activity,
        'individual_notes': individual_notes,     
        'relationship_data': relationship_data,     
        'policies': policies,     
    })


def delete_individual(request, individual_id):
    individual = get_object_or_404(Individuals, id=individual_id)
    individual.delete()
    return redirect('search_individuals_list') 

# Policy


@require_http_methods(["POST"])
def save_policy(request):
    record_type = request.POST.get('recordType')

    if record_type == 'existing':
        individual_id = request.POST.get('individual_id')
        if not individual_id:
            return JsonResponse({'error': 'Individual ID is required for existing type'}, status=400)
        individual = get_object_or_404(Individuals, id=individual_id)
    
    elif record_type == 'new':
        individual = Individuals.objects.create(
            first_name=request.POST.get('first_name'),
            middle_name=request.POST.get('middle_name', ''),
            last_name=request.POST.get('last_name'),
            individual_type=request.POST.get('individual_type'),
            email=request.POST.get('email'),
            servicing_agent_id=request.POST.get('servicing_agent_id') or None,
            business_phone=request.POST.get('business_phone'),
            business_ext=request.POST.get('business_ext'),
            home_phone=request.POST.get('home_phone'),
            home_ext=request.POST.get('home_ext'),
            cell_phone=request.POST.get('cell_phone'),
            cell_ext=request.POST.get('cell_ext')
        )
    else:
        return JsonResponse({'error': 'Invalid record type'}, status=400)


    policy = Policy.objects.create(
        individual=individual,
        carrier_id=request.POST.get('carrier'),
        policy_number=request.POST.get('policy_number'),
        status=request.POST.get('status'),
        coverage_type=request.POST.get('coverage_type'),
        effective_date=request.POST.get('effective_date') or None,
        agent_id=request.POST.get('affiliate_agent_id') or None,
    )

    return JsonResponse({'success': True})

def search_policy(request):
    carriers = Carrier.objects.all()
    policy = Policy.objects.all()
    return render(request, 'policy/searchpolicy.html',{
        'carriers': carriers,
        'policy':policy
    })


def advanced_policy(request):
    return render(request, 'policy/advancedpolicy.html')

def saved_policy(request):
    return render(request, 'policy/savedpolicy.html')


def policy_tab(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    carriers = Carrier.objects.all()
    policy_details, _ = PolicyDetails.objects.get_or_create(policy_name=policy)
    agents = Agent.objects.all()
    policy_activity = PolicyActivity.objects.filter(policy_name=policy)
    policy_notes = PolicyNotes.objects.filter(policy_name=policy)
    policy_coverage, _ = PolicyCoverage.objects.get_or_create(policy_name=policy)
    carrier_products = []
    if policy.carrier:
        carrier_products = CarrierProduct.objects.filter(carrier=policy.carrier)

    if request.method == 'POST':
        # --- Policy Details Form ---
        if 'carrier' in request.POST:
            carrier_id = request.POST.get('carrier')
            if carrier_id:
                policy.carrier = Carrier.objects.get(id=carrier_id)
            policy.policy_number = request.POST.get('policy_number')
            policy.status = request.POST.get('status')
            policy.coverage_type = request.POST.get('coverage_type')
            policy.effective_date = request.POST.get('effective_date') or None
            agent_id = request.POST.get('affiliates_agent_id')
            if agent_id:
                policy.agent = Agent.objects.get(id=agent_id)
            policy.save()

            policy_details.project_code = request.POST.get('project_code')
            policy_details.pay_frequency = request.POST.get('pay_frequency')  or ''
            policy_details.lives = request.POST.get('lives')  or ''
            policy_details.premium = request.POST.get('premium')  or ''
            policy_details.app_submit_date = request.POST.get('app_submit_date') or None
            policy_details.renewal_date = request.POST.get('renewal_date') or None
            policy_details.term_date = request.POST.get('term_date') or None
            policy_details.pay_method = request.POST.get('pay_method')  or ''
            policy_details.notes = request.POST.get('notes')  or ''
            policy_details.member_id = request.POST.get('member_id')  or ''
            policy_details.election = request.POST.get('election')  or ''
            policy_details.election_notes = request.POST.get('election_notes')  or ''
            policy_details.who_is_covered = 'who_is_covered' in request.POST
            signed_by_id = request.POST.get('signed_by_id')
            if signed_by_id:
                policy_details.signed_by = Agent.objects.get(id=signed_by_id)
            additional_agent_id = request.POST.get('additional_agents_id')
            if additional_agent_id:
                policy_details.additional_agent = Agent.objects.get(id=additional_agent_id)
            policy_details.save()

            return redirect('policy_tab', policy_id=policy_id)

        # --- Activity Form ---
        if request.POST.get('activity_subject'):
            activity_id = request.POST.get('activity_id')
            if activity_id:
                policy_activity_obj = PolicyActivity.objects.get(id=activity_id)
            else:
                policy_activity_obj = PolicyActivity(policy_name=policy)

            policy_activity_obj.subject = request.POST.get('activity_subject')
            policy_activity_obj.notes = request.POST.get('activity_notes')
            policy_activity_obj.status = request.POST.get('activity_status')
            policy_activity_obj.follow_up_team = request.POST.get('follow_up_team')
            policy_activity_obj.due_date = request.POST.get('due_date') == 'on'
            policy_activity_obj.activity_date = request.POST.get('activity_date') or None
            policy_activity_obj.priority = request.POST.get('priority')
            policy_activity_obj.type = request.POST.get('type')
            policy_activity_obj.method = request.POST.get('method')
            if request.FILES.get('attachment'):
                policy_activity_obj.attachment = request.FILES.get('attachment')
            policy_activity_obj.save()

            return redirect('policy_tab', policy_id=policy_id)

        # --- Notes Form ---
        if request.POST.get('note_subject'):
            note_id = request.POST.get('note_id')
            if note_id:
                policy_note = PolicyNotes.objects.get(id=note_id)
            else:
                policy_note = PolicyNotes(policy_name=policy)

            policy_note.subject = request.POST.get('note_subject')
            policy_note.notes = request.POST.get('note_notes')
            policy_note.pin_note = request.POST.get('pin_note') == 'on'
            if request.FILES.get('attachment'):
                policy_note.attachment = request.FILES.get('attachment')
            policy_note.save()

            return redirect('policy_tab', policy_id=policy_id)
        
        # ----- Coverage -----
        
        if request.POST.get('coverage_status') or request.POST.get('carrier_product'):
            policy_coverage.carrier_product_id = request.POST.get('carrier_product') or None
            policy_coverage.coverage_status = request.POST.get('coverage_status') or ''
            policy_coverage.coverage_effective_date = request.POST.get('coverage_effective_date') or None
            policy_coverage.coverage_premium = request.POST.get('coverage_premium') or None
            policy_coverage.coverage_renewal_date = request.POST.get('coverage_renewal_date') or None
            policy_coverage.coverage_renewal = request.POST.get('coverage_renewal') or None
            policy_coverage.coverage_lives = request.POST.get('coverage_lives') or None
            policy_coverage.coverage_termination_policy = request.POST.get('coverage_termination_policy') or ''
            policy_coverage.coinsurance = request.POST.get('coinsurance') or ''
            policy_coverage.deductible = request.POST.get('deductible') or None
            policy_coverage.deductible_family = request.POST.get('deductible_family') or None
            policy_coverage.max_out_of_pocket = request.POST.get('max_out_of_pocket') or None
            policy_coverage.max_out_of_pocket_family = request.POST.get('max_out_of_pocket_family') or None
            policy_coverage.out_of_network_costs = request.POST.get('out_of_network_costs') or ''
            policy_coverage.annual_maximum = request.POST.get('annual_maximum') or None
            policy_coverage.lifetime_maximum = request.POST.get('lifetime_maximum') or None
            policy_coverage.rx_tier1 = request.POST.get('rx_tier1') or ''
            policy_coverage.rx_tier2 = request.POST.get('rx_tier2') or ''
            policy_coverage.rx_tier3 = request.POST.get('rx_tier3') or ''
            policy_coverage.rx_tier4 = request.POST.get('rx_tier4') or ''
            policy_coverage.rx_tier5 = request.POST.get('rx_tier5') or ''
            policy_coverage.single_rate = request.POST.get('single_rate') or None
            policy_coverage.plus_spouse_rate = request.POST.get('plus_spouse_rate') or None
            policy_coverage.plus_children_rate = request.POST.get('plus_children_rate') or None
            policy_coverage.family_rate = request.POST.get('family_rate') or None
            policy_coverage.pharmacy_network = request.POST.get('pharmacy_network') or ''
            policy_coverage.provider_network = request.POST.get('provider_network') or ''
            policy_coverage.coverage_notes = request.POST.get('coverage_notes') or ''
            policy_coverage.fees = request.POST.get('fees') or ''
            policy_coverage.save()

            return redirect('policy_tab', policy_id=policy_id)

    return render(request, 'policy/policytab.html', {
        'policy_id': policy_id,
        'policy': policy,
        'policy_details': policy_details,
        'carriers': carriers,
        'agents': agents,
        'policy_activity': policy_activity,
        'policy_notes': policy_notes,
        'policy_coverage':policy_coverage,
        'carrier_products': carrier_products,
    })

@require_POST
def update_policy(request):
    policy_id = request.POST.get('policy_id')
    record_type = request.POST.get('record_type')

    policy = get_object_or_404(Policy, id=policy_id)

    if record_type == 'existing':
        individual_id = request.POST.get('individual_id')
        individual = get_object_or_404(Individuals, id=individual_id)
        policy.individual = individual
        policy.save()
        return redirect('policy_tab', policy_id=policy.id)

    elif record_type == 'new':
        individual = Individuals.objects.create(
            first_name=request.POST.get('first_name'),
            middle_name=request.POST.get('middle_name'),
            last_name=request.POST.get('last_name'),
            individual_type=request.POST.get('individual_type'),
            email=request.POST.get('email'),
            business_phone=request.POST.get('business_phone'),
            business_ext=request.POST.get('business_ext'),
            home_phone=request.POST.get('home_phone'),
            home_ext=request.POST.get('home_ext'),
            cell_phone=request.POST.get('cell_phone'),
            cell_ext=request.POST.get('cell_ext'),
            servicing_agent_id=request.POST.get('servicing_agent_id') or None
        )
        policy.individual = individual
        policy.save()
        return redirect('policy_tab', policy_id=policy.id)

    return redirect('policy_tab', policy_id=policy.id)


def add_carrier_product(request):
    if request.method == 'POST':
        carrier_id = request.POST.get('carrier')  
        coverage_type = request.POST.get('coverage_type')
        product_name = request.POST.get('product_name')
        description = request.POST.get('product_description')
        effective_date = request.POST.get('product_effective_date') or None
        term_date = request.POST.get('product_term_date') or None

        if carrier_id and product_name:
            product = CarrierProduct.objects.create(
                carrier_id=carrier_id,
                coverage_type=coverage_type,
                product_name=product_name,
                description=description,
                effective_date=effective_date,
                term_date=term_date
            )
            return JsonResponse({
                'success': True,
                'product_id': product.id,
                'product_name': product.product_name
            })
        else:
            return JsonResponse({'success': False, 'error': 'Missing required fields.'})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


def delete_policy(request, policy_id):
    policy = get_object_or_404(Policy, id=policy_id)
    policy.delete()
    return redirect('search_policy')  



def custom_fields(request):
    return render(request, 'carrier/customfields.html')



def agent_column_settings(request):

    return render(request, 'agency/agentcolumnsettings.html')











