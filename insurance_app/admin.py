# insurance_app/admin.py

from django.contrib import admin
from .models import Customer, Policy

class PolicyInline(admin.TabularInline):
    model = Policy
    extra = 1

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tc_id', 'phone', 'job', 'birth_date', 'city') # 'referans' kaldırıldı
    search_fields = ('name', 'tc_id', 'phone', 'city', 'job')
    inlines = [PolicyInline]

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('customer', 'policy_type', 'insurance_company', 'plate', 'due_date')
    search_fields = ('customer__name', 'policy_type', 'insurance_company', 'plate')
    list_filter = ('policy_type', 'insurance_company')