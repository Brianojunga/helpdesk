from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    STAFF_ROLES = [
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('owner', 'Owner'),
        ('customer', 'Customer')
    ]
    company = models.ForeignKey(
        'tickets.Company', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='company_staff'
        )
    role = models.CharField(max_length=20, choices=STAFF_ROLES, default='customer')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

