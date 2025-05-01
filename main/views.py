from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from django.shortcuts import get_object_or_404



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


def carrier_detail(request,pk):
    carrier_details = get_object_or_404(Carrier, pk=pk)
    return render(request, 'carrier/carrierdetail.html',{'carrier_details':carrier_details})

def individuals_view(request):
    return render(request, 'carrierindividuals.html')


def custom_fields(request):
    return render(request, 'carrier/customfields.html')
