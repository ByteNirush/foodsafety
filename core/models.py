from django.contrib.auth.models import AbstractUser
from django.db import models

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

    def __str__(self):
        return self.email