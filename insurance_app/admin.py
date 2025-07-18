# insurance_app/admin.py
from django.contrib import admin
from .models import Customer, Policy

# Policy modelini Django Admin paneline kaydet
admin.site.register(Policy)

# Müşteri detay sayfasında poliçeleri inline göstermek için
class PolicyInline(admin.TabularInline):
    model = Policy
    extra = 1 # Yeni poliçe eklemek için kaç boş satır gösterileceği

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [PolicyInline]
    # list_display'den 'plate' gibi Policy modeline taşınan alanları kaldırıyoruz
    list_display = ('name', 'tc_id', 'phone', 'city', 'job', 'referans') # 'plate' kaldırıldı
    search_fields = ('name', 'tc_id', 'phone', 'referans') # arama alanlarını da güncelleyebiliriz
    list_filter = ('city', 'job')