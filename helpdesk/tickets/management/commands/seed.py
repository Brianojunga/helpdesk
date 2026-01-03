from django.core.management import BaseCommand
from tickets.models import Ticket, Company, TicketResolution
from django.contrib.auth import get_user_model
from faker import Faker
import random
import re

User = get_user_model()

def status(users, company):
    status_choice = random.choice((['open', 'in_progress', 'closed']))
    assigned_to = None
    eligible_agents = []
    for user in users:
        if user.company == company and user.role in ['agent', 'admin'] :
            eligible_agents.append(user)
    if status_choice in ['in_progress', 'closed']:
        assigned_to = random.choice(eligible_agents) if eligible_agents else None
    return status_choice, assigned_to


def resolution_message(tickets, faker):
    message = faker.sentence()
    for ticket in tickets:
        if ticket.status == 'closed':
            TicketResolution.objects.create(
                ticket=ticket,
                message=message
            )

def assign_company(users, company):
    roles = ['admin', 'agent', 'owner', 'customer']
    role = random.choice(roles)

    owner_exists = any(
        user.role == 'owner' and user.company == company for user in users
    )

    if owner_exists and role == 'owner':
        role = random.choice(['admin', 'agent', 'customer'])

    if role == 'customer':
        company = None

    return role, company

class Command(BaseCommand):
    help = 'Seed the database with sample tickets'
    

    def handle(self, *args, **kwargs):
        faker = Faker()

        #create sample companies
        companies = []
        for _ in range(5):
            name = faker.company()
            mail = faker.email()
            phone = faker.phone_number()
            digits_only = re.sub(r'\D', '', phone)
            phone_12 = digits_only[:12]
            address = faker.address()
            description = faker.sentence()
            company = Company.objects.create(name=name, email=mail, phone=phone_12, address=address, description=description)
            companies.append(company)
        self.stdout.write(self.style.SUCCESS('Created 5 sample companies.'))

        # Create sample users
        users = []
        for _ in range (30):
            username = faker.user_name()
            email = faker.email()
            role, place_of_work = assign_company(users, random.choice(companies))
            user = User.objects.create(
                username=username, 
                email=email, password='password123', 
                company=place_of_work, 
                role=role
            )
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created 30 sample users.'))

        # Create sample tickets
        tickets = []
        for _ in range(100):
            if random.choice([True, False]):
                user = random.choice(users)
                first_name = ''
                last_name = '' 
                email = ''
            else:
                user = None
                first_name = faker.first_name()
                last_name = faker.last_name()
                email = faker.email()
            company = random.choice(companies)
            subject = faker.sentence(nb_words=6)
            description = faker.paragraph(nb_sentences=3)
            status_choice, assigned_to = status(users, company)
            priority =  random.randint(0, 4)
            ticket = Ticket.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                description=description,
                status=status_choice,
                assigned_to=assigned_to,
                company=company,
                priority=priority
            )
            tickets.append(ticket)
        resolution_message(tickets, faker)
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with sample tickets and resolution messages.'))

