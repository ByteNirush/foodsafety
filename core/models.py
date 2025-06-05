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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    name = models.CharField(max_length=200)
    manufacture_date = models.DateField()
    expire_date = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('Available', 'Available'),
        ('Donated', 'Donated'),
        ('Thrown', 'Thrown'),
    ], default='Available')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (by {self.user.email if self.user else 'No User'})"
    
class Donation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='donations', null=True, blank=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    food_items = models.TextField()
    pickup_location = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Donation by {self.user.email} at {self.created_at}"