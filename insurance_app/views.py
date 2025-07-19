# insurance_app/views.py

from django.shortcuts import render
from django.db.models import Q
from .models import Customer, Policy
import unicodedata

def customer_list(request):
    customers = Customer.objects.prefetch_related('policies').all()

    search_name = request.GET.get('search_name', '')
    filter_policy = request.GET.get('filter_policy', '')
    filter_company = request.GET.get('filter_company', '')

    show_customers = False
    if search_name or filter_policy or filter_company:
        show_customers = True
        if search_name:
            normalized_search_name = unicodedata.normalize('NFKD', search_name).encode('ascii', 'ignore').decode('utf-8').upper()
            customers = customers.filter(Q(name__icontains=normalized_search_name) | Q(tc_id__icontains=normalized_search_name))

        if filter_policy:
            customers = customers.filter(policies__policy_type=filter_policy)

        if filter_company:
            customers = customers.filter(policies__insurance_company=filter_company)

        if not customers.exists():
            show_customers = False


    all_policy_types = Policy.objects.values_list('policy_type', flat=True).distinct().order_by('policy_type')
    all_insurance_companies = Policy.objects.values_list('insurance_company', flat=True).distinct().order_by('insurance_company')

    policy_types_for_template = []
    for pt in all_policy_types:
        policy_types_for_template.append({
            'name': pt,
            'selected': (pt == filter_policy)
        })

    insurance_companies_for_template = []
    for ic in all_insurance_companies:
        insurance_companies_for_template.append({
            'name': ic,
            'selected': (ic == filter_company)
        })

    context = {
        'customers': customers,
        'search_name': search_name,
        'filter_policy': filter_policy,
        'filter_company': filter_company,
        'policy_types': policy_types_for_template,
        'insurance_companies': insurance_companies_for_template,
        'show_customers': show_customers,
    }
    return render(request, 'insurance_app/customer_list.html', context)