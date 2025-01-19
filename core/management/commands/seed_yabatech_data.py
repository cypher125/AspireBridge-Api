from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from opportunities.models import Opportunity
from applications.models import Application
from notifications.models import Notification
from faker import Faker
import random
from datetime import timedelta

User = get_user_model()
fake = Faker()  # Use default locale

# Add Nigerian names and patterns
nigerian_first_names = [
    'Oluwaseun', 'Chioma', 'Adebayo', 'Ngozi', 'Olayinka', 'Chidi', 'Folake', 
    'Babatunde', 'Aisha', 'Emmanuel', 'Blessing', 'Oluwafemi', 'Chinua', 'Yetunde',
    'Obinna', 'Folashade', 'Kayode', 'Chidinma', 'Oluwadamilola', 'Temitope'
]

nigerian_last_names = [
    'Adebayo', 'Okonkwo', 'Okafor', 'Adeyemi', 'Oluwole', 'Eze', 'Adegoke', 
    'Ogunleye', 'Nnamdi', 'Afolabi', 'Oladipo', 'Nwachukwu', 'Adeleke', 'Igwe',
    'Olayinka', 'Chukwu', 'Adeniyi', 'Ogunlesi', 'Babangida', 'Ogunbiyi'
]

def generate_nigerian_name():
    return f"{random.choice(nigerian_first_names)} {random.choice(nigerian_last_names)}"

def generate_nigerian_phone():
    prefixes = ['0803', '0805', '0806', '0807', '0813', '0814', '0816', '0903', '0906']
    return f"{random.choice(prefixes)}{''.join([str(random.randint(0, 9)) for _ in range(7)])}"

class Command(BaseCommand):
    help = 'Seeds the database with Yabatech-specific test data'

    def handle(self, *args, **kwargs):
        # Clear existing data
        self.stdout.write('Clearing existing data...')
        User.objects.all().delete()
        Opportunity.objects.all().delete()
        Application.objects.all().delete()

        self.stdout.write('Starting Yabatech data seeding...')

        # Create admin users
        admins = []
        admin_departments = [
            'Student Affairs',
            'Academic Affairs',
            'Industrial Relations',
            'Career Services',
            'Alumni Relations'
        ]
        
        for dept in admin_departments:
            email = f"{dept.lower().replace(' ', '.')}@yabatech.edu.ng"
            admin = User.objects.create_superuser(
                email=email,
                username=email,
                password='Admin123!',
                name=f'{dept} Administrator',
                role='administrator',
                organization_details=f'Yaba College of Technology - {dept}',
                phone_number=fake.phone_number(),
                location='Yaba, Lagos'
            )
            admins.append(admin)
            self.stdout.write(f'Created admin: {email}')

        # Create students
        students = []
        departments = [
            'Computer Science',
            'Accountancy',
            'Business Administration',
            'Electrical Engineering',
            'Civil Engineering',
            'Architecture',
            'Marketing',
            'Mass Communication',
            'Food Technology',
            'Chemical Engineering'
        ]

        for _ in range(50):  # Create 50 students
            dept = random.choice(departments)
            matric = f'YCT/{str(random.randint(20, 23)).zfill(2)}/{random.randint(100000, 999999)}'
            
            student = User.objects.create_user(
                email=f'{matric.lower()}@students.yabatech.edu.ng',
                username=matric,
                password='Student123!',
                name=generate_nigerian_name(),  # Use Nigerian name generator
                role='student',
                matriculation_number=matric,
                course=dept,
                year_of_study=random.randint(1, 4),
                phone_number=generate_nigerian_phone(),  # Use Nigerian phone generator
                location=random.choice([
                    'Yaba', 'Surulere', 'Ikeja', 'Gbagada', 'Maryland', 
                    'Oshodi', 'Mushin', 'Shomolu', 'Bariga', 'Ojota'
                ]),
                description=fake.text(max_nb_chars=200)
            )
            students.append(student)
            self.stdout.write(f'Created student: {matric}')

        # Create opportunities
        opportunities = []
        nigerian_companies = [
            'Access Bank', 'GTBank', 'MTN Nigeria', 'Dangote Group', 'Flutterwave',
            'Paystack', 'Nigerian Breweries', 'Andela Nigeria', 'KPMG Nigeria',
            'PwC Nigeria', 'Deloitte Nigeria', 'Shell Nigeria', 'Chevron Nigeria',
            'Main One', 'Interswitch', 'SystemSpecs', 'Union Bank', 'First Bank',
            'Zenith Bank', 'UBA', 'Sterling Bank', 'FCMB', 'Wema Bank', 'Fidelity Bank',
            'Total Nigeria', 'Globacom', '9mobile', 'Airtel Nigeria', 'IBM Nigeria',
            'Microsoft Nigeria', 'Google Nigeria', 'Jumia Nigeria', 'Konga'
        ]

        opportunity_types = [
            'internship',
            'full_time',
            'part_time',
            'industrial_training',
            'graduate_trainee'
        ]

        lagos_locations = [
            'Victoria Island', 'Ikoyi', 'Lekki', 'Yaba', 'Surulere',
            'Ikeja', 'Maryland', 'Gbagada', 'Apapa', 'Marina'
        ]

        for _ in range(30):  # Create 30 opportunities
            company = random.choice(nigerian_companies)
            type_ = random.choice(opportunity_types)
            start_date = timezone.now() + timedelta(days=random.randint(14, 45))  # Start in 2-6 weeks
            deadline = start_date + timedelta(days=random.randint(30, 90))  # Deadline after start date
            
            description = '\n'.join([
                'About the Role:',
                fake.text(max_nb_chars=300),
                '\nRequirements:',
                '- Currently enrolled in Yaba College of Technology',
                f'- Studying {", ".join(random.sample(departments, 3))} or related field',
                '- Strong academic performance',
                '- Excellent communication skills',
                '\nBenefits:',
                '- Competitive stipend',
                '- Professional development',
                '- Mentorship opportunity',
                '- Possible conversion to full-time',
                f'\nSalary Range: NGN {random.randint(50, 250)}k - {random.randint(251, 500)}k monthly'
            ])

            opportunity = Opportunity.objects.create(
                title=f'{company} {type_.replace("_", " ").title()} Program',
                organization=company,
                description=description,
                type=type_,
                location=f'{random.choice(lagos_locations)}, Lagos',
                requirements='\n'.join([
                    '- Currently enrolled in Yaba College of Technology',
                    f'- Studying {", ".join(random.sample(departments, 3))} or related field',
                    '- Strong academic performance',
                    '- Excellent communication skills',
                    '- Good team player',
                ]),
                start_date=start_date,  # Add start date
                application_deadline=deadline,
                created_by=random.choice(admins),
                status='active',
            )
            opportunities.append(opportunity)
            self.stdout.write(f'Created opportunity: {opportunity.title}')

        # Create applications and notifications
        application_statuses = ['pending', 'under_review', 'shortlisted', 'accepted', 'rejected']
        
        for student in students:
            # Each student applies to 2-5 opportunities
            for opportunity in random.sample(opportunities, random.randint(2, 5)):
                status = random.choice(application_statuses)
                
                application = Application.objects.create(
                    user=student,
                    opportunity=opportunity,
                    status=status,
                    cover_letter='\n'.join([
                        f'Dear {opportunity.organization} Hiring Team,',
                        '',
                        'I am writing to express my strong interest in the ' +
                        f'{opportunity.title} position. As a {student.year_of_study}rd year ' +
                        f'{student.course} student at Yaba College of Technology, ' +
                        'I believe I would be an excellent candidate for this role.',
                        '',
                        fake.text(max_nb_chars=300),
                        '',
                        'Thank you for considering my application.',
                        '',
                        f'Best regards,\n{student.name}'
                    ]),
                    documents=[
                        {
                            "name": "Resume.pdf",
                            "url": f"https://storage.aspirebridge.ng/documents/{student.id}/resume.pdf"
                        },
                        {
                            "name": "Transcript.pdf",
                            "url": f"https://storage.aspirebridge.ng/documents/{student.id}/transcript.pdf"
                        }
                    ],
                    applied_at=timezone.now() - timedelta(days=random.randint(1, 30))
                )
                
                # Create application submission notification
                Notification.objects.create(
                    user=student,
                    title=f'Application Submitted - {opportunity.title}',
                    message=f'Your application for {opportunity.title} at {opportunity.organization} has been submitted successfully.',
                    type='application_update'
                )

                # Create notification for organization admin
                Notification.objects.create(
                    user=opportunity.created_by,
                    title=f'New Application Received - {opportunity.title}',
                    message=f'{student.name} has applied for {opportunity.title}',
                    type='application_update'
                )
                
                # Add interview date and notifications for shortlisted applications
                if status in ['shortlisted', 'accepted']:
                    interview_date = timezone.now() + timedelta(days=random.randint(5, 15))
                    application.interview_date = interview_date
                    application.save()

                    # Create interview notification for student
                    Notification.objects.create(
                        user=student,
                        title=f'Interview Scheduled - {opportunity.title}',
                        message=f'Your interview for {opportunity.title} at {opportunity.organization} has been scheduled for {interview_date.strftime("%B %d, %Y at %I:%M %p")}.',
                        type='interview'
                    )

                    # Create interview notification for admin
                    Notification.objects.create(
                        user=opportunity.created_by,
                        title=f'Interview Scheduled - {opportunity.title}',
                        message=f'Interview scheduled with {student.name} for {opportunity.title} on {interview_date.strftime("%B %d, %Y at %I:%M %p")}.',
                        type='interview'
                    )

                # Create status update notifications for non-pending applications
                if status != 'pending':
                    status_message = {
                        'under_review': 'is now under review',
                        'shortlisted': 'has been shortlisted',
                        'accepted': 'has been accepted',
                        'rejected': 'has been rejected'
                    }
                    
                    Notification.objects.create(
                        user=student,
                        title=f'Application Status Update - {opportunity.title}',
                        message=f'Your application for {opportunity.title} at {opportunity.organization} {status_message[status]}.',
                        type='application_update'
                    )

                self.stdout.write(f'Created application and notifications: {student.name} -> {opportunity.title}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded Yabatech data')) 