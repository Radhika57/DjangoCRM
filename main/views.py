from django.shortcuts import render, redirect # type: ignore
from django.http import JsonResponse # type: ignore
from .models import *
from django.shortcuts import get_object_or_404 # type: ignore



def dashboard(request):
    return render(request, "dashboard/index.html")


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

    try:
        carrier_details = carrier.carrier_details
    except CarrierDetails.DoesNotExist:
        carrier_details = None

    carrier_phones = CarrierPhone.objects.filter(carrier=carrier)
    phone_dict = {phone.phone_type.lower(): phone for phone in carrier_phones}
    addresses = CarrierAddress.objects.filter(carrier=carrier)
    carrier_forms = CarrierFormName.objects.filter(carrier=carrier)  
    activities = CarrierActivity.objects.filter(carrier=carrier)  
    notess = CarrierNotes.objects.filter(carrier=carrier)  
    products = CarrierProduct.objects.filter(carrier=carrier)
    websites = CarrierWebsite.objects.filter(carrier=carrier)
    
    if request.method == 'POST':
        # ------------------- Handle Carrier Activity -------------------
        if 'subject' in request.POST and 'activity_date' in request.POST:
            CarrierActivity.objects.create(
                carrier=carrier,
                subject=request.POST.get('subject'),
                notes=request.POST.get('notes'),
                status=request.POST.get('status'),
                follow_up_user=request.POST.get('follow_up_user'),
                follow_up_team=request.POST.get('follow_up_team'),
                due_date=request.POST.get('due_date') or None,
                activity_date=request.POST.get('activity_date'),
                priority=request.POST.get('priority'),
                activity_type=request.POST.get('activity_type'),
                method=request.POST.get('method'),
                attachment=request.FILES.get('attachment')
            )
            return redirect('carrier_detail', carrier_id=carrier.id)

        # ------------------- Handle Carrier Notes -------------------
        if 'subject' in request.POST and 'notes' in request.POST and 'activity_date' not in request.POST:
            CarrierNotes.objects.create(
                carrier=carrier,
                subject=request.POST.get('subject'),
                notes=request.POST.get('notes'),
                attachment=request.FILES.get('attachment')
            )
            return redirect('carrier_detail', carrier_id=carrier.id)

        # ------------------- Handle Carrier Form Name -------------------
        if 'form_name' in request.POST and 'form_file' in request.FILES:
            CarrierFormName.objects.create(
                carrier=carrier,
                form_name=request.POST.get('form_name'),
                year=request.POST.get('year'),
                form_number=request.POST.get('form_number'),
                coverage_type=request.POST.get('coverage_type'),
                form_file=request.FILES.get('form_file')
            )
            return redirect('carrier_detail', carrier_id=carrier.id)

        # ------------------- Handle Carrier Details -------------------
        abbreviation = request.POST.get('abbreviation')
        security_groups = request.POST.getlist('security_groups[]')
        carrier_status = request.POST.get('carrier_status')

        if carrier_details:
            carrier_details.abbreviation = abbreviation
            carrier_details.security_groups = security_groups
            carrier_details.carrier_status = carrier_status
            carrier_details.save()
        else:
            CarrierDetails.objects.create(
                carrier=carrier,
                abbreviation=abbreviation,
                security_groups=security_groups,
                carrier_status=carrier_status
            )

        # ------------------- Save Phones -------------------
        phone_types = ['Business', 'Home', 'Cell', 'Fax']
        for phone_type in phone_types:
            number = request.POST.get(f'{phone_type.lower()}_phone')
            ext = request.POST.get(f'{phone_type.lower()}_ext')

            try:
                phone_obj = CarrierPhone.objects.get(carrier=carrier, phone_type=phone_type)
                if number:
                    phone_obj.number = number
                    phone_obj.extension = ext
                    phone_obj.save()
                else:
                    phone_obj.delete()  
            except CarrierPhone.DoesNotExist:
                if number:
                    CarrierPhone.objects.create(
                        carrier=carrier,
                        phone_type=phone_type,
                        number=number,
                        extension=ext
                    )


        # ------------------- Save/Update Address -------------------
        address_type = request.POST.get('address_type')
        primary = request.POST.get('primary_address') == 'on'
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        zip_code = request.POST.get('zip_code')
        city = request.POST.get('city')
        state = request.POST.get('state')
        county = request.POST.get('county')
        description = request.POST.get('description')

        if address1 and zip_code and city and state:
            address_obj = addresses.filter(primary=True).first()
            if address_obj:
                address_obj.address_type = address_type
                address_obj.primary = primary
                address_obj.address1 = address1
                address_obj.address2 = address2
                address_obj.zip_code = zip_code
                address_obj.city = city
                address_obj.state = state
                address_obj.county = county
                address_obj.description = description
                address_obj.save()
            else:
                CarrierAddress.objects.create(
                    carrier=carrier,
                    address_type=address_type,
                    primary=primary,
                    address1=address1,
                    address2=address2,
                    zip_code=zip_code,
                    city=city,
                    state=state,
                    county=county,
                    description=description
                )
                
            # ------------------- Handle Carrier Product -------------------
        if 'product_name' in request.POST and 'coverage_type' in request.POST:
            states = request.POST.getlist('states[]')

            product = CarrierProduct.objects.create(
                carrier=carrier,
                coverage_type=request.POST.get('coverage_type'),
                product_name=request.POST.get('product_name'),
                effective_date=request.POST.get('product_effective_date') or None,
                term_date=request.POST.get('product_term_date') or None,
                description=request.POST.get('description'),
                benefit_summary=request.FILES.get('benefit_summary'),
                plan_grid=request.FILES.get('plan_grid'),
                brochure=request.FILES.get('brochure'),
                states=states  
                # modified_by=request.user
            )
            product.save()
        
        # ------------------- Handle Carrier Website -------------------
        if request.POST.get('website_name'):
            CarrierWebsite.objects.create(
                carrier=carrier,
                website_name=request.POST.get('website_name'),
                url=request.POST.get('url'),
                username=request.POST.get('username'),
                password=request.POST.get('password'),
            )

        return redirect('carrier_detail', carrier_id=carrier.id)

    context = {
        'carrier': carrier,
        'carrier_details': carrier_details,
        'phone_dict': phone_dict,
        'primary_address': addresses.filter(primary=True).first(),
        'carrier_forms': carrier_forms,  
        'carrier_phones': carrier_phones,
        'addresses': addresses,
        'activities':activities,
        'notess':notess,
        'products': products,
        'websites': websites,
    }
    return render(request, 'carrier/carrierdetail.html', context)

def edit_carrier_address(request, address_id):
    address = get_object_or_404(CarrierAddress, id=address_id)

    if request.method == 'POST':
        address.address_type = request.POST.get('address_type')
        address.primary = request.POST.get('primary_address') == 'on'
        address.address1 = request.POST.get('address1')
        address.address2 = request.POST.get('address2')
        address.zip_code = request.POST.get('zip_code')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')
        address.county = request.POST.get('county')
        address.description = request.POST.get('description')
        address.save()

        return redirect('carrier_detail', carrier_id=address.carrier.id)

def delete_carrier_address(request, address_id):
    address = get_object_or_404(CarrierAddress, id=address_id)
    carrier_id = address.carrier.id  

    if request.method == 'POST':
        address.delete()
        return redirect('carrier_detail', carrier_id) 

    return redirect('carrier_detail', carrier_id)

def custom_fields(request):
    return render(request, 'carrier/customfields.html')

def search_agents(request):
    return render(request, 'agency/searchagency.html')

def manage_agencies(request):
    return render(request, 'agency/manageagencies.html')

def agent_column_settings(request):
    return render(request, 'agency/agentcolumnsettings.html')

def agency_detail(request, agency_id):
  
    return render(request, 'agency/agencydetail.html', {'agency_id': agency_id})

def agent_column_settings(request):
    return render(request, 'agency/agentcolumnsettings.html')


def advanced_search(request):
    return render(request, 'agency/advancedsearch.html')
def saved_searches(request):
    return render(request, 'agency/savedsearch.html')
def agency_client(request):
    return render(request, 'agency/agencyclient.html')

def policy_detail(request, policy_id):
    
    return render(request, 'policy/policydetail.html', {'policy_id': policy_id})
def agency_activity(request):
    return render(request, 'agency/agencyactivity.html')
def agency_note(request):
    return render(request, 'agency/agencynote.html')

def agency_eo(request):
    return render(request, 'agency/agencyeo.html')
def search_policy(request):
    return render(request, 'policy/searchpolicy.html')
def advanced_policy(request):
    return render(request, 'policy/advancedpolicy.html')

def saved_policy(request):
    return render(request, 'policy/savedpolicy.html')
def senior_select(request):
    return render(request, 'agency/seniorselect.html')
def payment_report(request):
    return render(request, 'policy/paymentreport.html')
def payment_report1(request):
    return render(request, 'policy/paymentreport1.html')









