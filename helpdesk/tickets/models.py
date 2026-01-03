from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils.text import slugify

# Create your models here.
User = get_user_model()

class Company(models.Model):
    name = models.CharField(max_length=35)
    slug = models.SlugField(unique=True)
    email = models.EmailField(blank=False, null=False)
    phone = models.CharField(blank=True, null=True, max_length=12)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        (0, 'None'),
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High')
    ]
    public_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False, null=False, blank=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')

    def __str__(self):
        if self.user:
            return f"{self.subject} by {self.user.username}"
        else:
            return f"{self.subject} by {self.first_name} {self.last_name}"

class TicketResolution(models.Model):
    ticket=models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='resolution')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Resolution for {self.ticket.public_id} with the subject {self.ticket.subject}'
    