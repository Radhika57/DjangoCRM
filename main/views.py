from django.shortcuts import render
from .models import Carrier


def dashboard(request):
    return render(request, "dashboard/index.html")


def carrier_list(request):
    carriers = Carrier.objects.all()
    return render(request, 'carrier/carrierlist.html', {'carriers': carriers})

def carrier_detail(request):
    return render(request, 'carrier/carrierdetail.html')

def individuals_view(request):
    return render(request, 'carrierindividuals.html')


