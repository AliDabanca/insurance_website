# insurance_app/models.py

from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, default='Bilinmiyor')
    tc_id = models.CharField(max_length=11, unique=True)
    birth_date = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, default='-')
    phone = models.CharField(max_length=20, default='-')
    job = models.CharField(max_length=50, default='-')
    referans = models.CharField(max_length=100, default='-')

    def __str__(self):
        return self.name

class Policy(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='policies') # Bu kısım önemli
    plate = models.CharField(max_length=20, default='-')
    license = models.CharField(max_length=50, default='-')
    policy_type = models.CharField(max_length=50, default='-')
    insurance_company = models.CharField(max_length=50, default='-')
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.customer.name} - {self.policy_type} ({self.insurance_company})"