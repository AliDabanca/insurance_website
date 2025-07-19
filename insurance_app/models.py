# insurance_app/models.py

from django.db import models
import unicodedata 

class Customer(models.Model):
    name = models.CharField(max_length=100)
    tc_id = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    job = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    # 'referans' alanı KESİNLİKLE BURADA OLMAMALI

    def save(self, *args, **kwargs):
        if self.name:
            self.name = unicodedata.normalize('NFKD', self.name).encode('ascii', 'ignore').decode('utf-8').upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Policy(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='policies')
    policy_type = models.CharField(max_length=50)
    insurance_company = models.CharField(max_length=50, blank=True, null=True)
    plate = models.CharField(max_length=20, blank=True, null=True)
    license = models.CharField(max_length=50, blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.customer.name} - {self.policy_type}"