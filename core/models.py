from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    admin_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'custom_user'

    def __str__(self):
        return self.email