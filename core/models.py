from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    admin_code = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True, choices=[
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
        ('Prefer not to say', 'Prefer not to say'),
    ])
    dob = models.DateField(blank=True, null=True)
    medical_condition = models.CharField(max_length=100, blank=True, null=True, choices=[
        ('None', 'None'),
        ('Diabetes', 'Diabetes'),
        ('Hypertension', 'Hypertension'),
        ('Asthma', 'Asthma'),
        ('Allergy (Peanut)', 'Allergy (Peanut)'),
        ('Allergy (Lactose)', 'Allergy (Lactose)'),
        ('Heart Disease', 'Heart Disease'),
        ('Other', 'Other'),
    ])
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

class Product(models.Model):
    name = models.CharField(max_length=200)
    manufacture_date = models.DateField()
    expire_date = models.DateField()

    def __str__(self):
        return self.name