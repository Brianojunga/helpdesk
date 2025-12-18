from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class staff(models.Model):
    STAFF_ROLES = [
        ('admin', 'Admin'),
        ('agent', 'Agent'),
        ('manager', 'Manager')
    ]