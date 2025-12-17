from django.core.management import BaseCommand
from tickets.models import Ticket, Company
from django.contrib.auth.models import User
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Seed the database with sample tickets'

    def handle(self, *args, **kwargs):
        faker = Faker()

        #create sample companies
        companies = []
        for _ in range(5):
            name = faker.company()
            company = Company.objects.create(name=name)
            companies.append(company)

        # Create sample users
        users = []
        for _ in range (10):
            username = faker.user_name()
            email = faker.email()
            user = User.objects.create_user(username=username, email=email, password='password123')
            users.append(user)
        self.stdout.write(self.style.SUCCESS('Created 10 sample users.'))

        # Create sample tickets
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
            status = random.choice(['open', 'in_progress', 'closed'])
            Ticket.objects.create(
                user=user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                subject=subject,
                description=description,
                status=status,
                company=company
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded the database with sample tickets.'))