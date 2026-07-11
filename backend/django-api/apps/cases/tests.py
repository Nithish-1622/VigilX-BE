from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.cases.models import FIR, Victim, Accused, ClueEntity, CrimeType, CaseStatus, ClueEntityType, GenderChoices
from apps.users.models import UserRole
import datetime
from django.utils import timezone

User = get_user_model()

class CaseAPITests(APITestCase):
    """
    Test suite verifying cases CRUD operations, RBAC, PII redactions,
    and clue-entity matching filters.
    """
    def setUp(self):
        # Create user personas
        self.investigator = User.objects.create_user(
            username='investigator_bob',
            password='Password123!',
            role=UserRole.INVESTIGATOR
        )
        self.policymaker = User.objects.create_user(
            username='policymaker_pat',
            password='Password123!',
            role=UserRole.POLICYMAKER
        )
        self.analyst = User.objects.create_user(
            username='analyst_ann',
            password='Password123!',
            role=UserRole.ANALYST
        )

        # Create basic case
        self.fir = FIR.objects.create(
            fir_number='FIR/2026/00001',
            crime_type=CrimeType.BURGLARY,
            incident_date_time=timezone.now() - datetime.timedelta(days=1),
            reported_date_time=timezone.now(),
            location='123 Main St',
            latitude=12.9716,
            longitude=77.5946,
            status=CaseStatus.UNDER_INVESTIGATION,
            description='Commercial burglary at a jewellery store.',
            officer_in_charge=self.investigator
        )

        # Register Victim
        self.victim = Victim.objects.create(
            fir=self.fir,
            name='Jane Doe',
            age=30,
            gender=GenderChoices.FEMALE,
            contact_number='+919999988888',
            address='456 Victim Ln',
            statement='He broke the window.'
        )

        # Register Accused
        self.accused = Accused.objects.create(
            fir=self.fir,
            name='John Robber',
            age=25,
            gender=GenderChoices.MALE,
            contact_number='+918888877777',
            address='789 Suspect Ave',
            criminal_history='Prior burglary arrest in 2024.'
        )

        # Register Clue
        self.clue = ClueEntity.objects.create(
            fir=self.fir,
            entity_type=ClueEntityType.PHONE_NUMBER,
            value='+918888877777',
            description='Accused cell phone number used near tower'
        )

    def test_case_creation_rbac(self):
        # Policymakers must be blocked from writing records
        self.client.force_authenticate(user=self.policymaker)
        url = reverse('cases-list')
        response = self.client.post(url, {
            'fir_number': 'FIR/2026/00002',
            'crime_type': CrimeType.THEFT,
            'incident_date_time': '2026-07-10T12:00:00Z',
            'reported_date_time': '2026-07-10T13:00:00Z',
            'location': 'Downtown Plaza',
            'description': 'Phone snatching.'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Investigators must be allowed
        self.client.force_authenticate(user=self.investigator)
        response = self.client.post(url, {
            'fir_number': 'FIR/2026/00002',
            'crime_type': CrimeType.THEFT,
            'incident_date_time': '2026-07-10T12:00:00Z',
            'reported_date_time': '2026-07-10T13:00:00Z',
            'location': 'Downtown Plaza',
            'description': 'Phone snatching.'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_policymaker_pii_redaction(self):
        # Retrieve detailed report as Investigator (can see full details)
        self.client.force_authenticate(user=self.investigator)
        url = reverse('cases-detail', kwargs={'pk': self.fir.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        victim_data = response.data['victims'][0]
        self.assertEqual(victim_data['contact_number'], '+919999988888')
        self.assertEqual(victim_data['address'], '456 Victim Ln')
        
        accused_data = response.data['accused'][0]
        self.assertEqual(accused_data['contact_number'], '+918888877777')
        self.assertEqual(accused_data['criminal_history'], 'Prior burglary arrest in 2024.')

        # Retrieve detailed report as Policymaker (should be redacted)
        self.client.force_authenticate(user=self.policymaker)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        victim_data = response.data['victims'][0]
        self.assertEqual(victim_data['contact_number'], '[REDACTED]')
        self.assertEqual(victim_data['address'], '[REDACTED]')
        self.assertEqual(victim_data['statement'], '[REDACTED]')
        
        accused_data = response.data['accused'][0]
        self.assertEqual(accused_data['contact_number'], '[REDACTED]')
        self.assertEqual(accused_data['address'], '[REDACTED]')
        self.assertEqual(accused_data['criminal_history'], '[REDACTED]')

    def test_clue_entity_search(self):
        self.client.force_authenticate(user=self.investigator)
        url = reverse('entities-list')
        # Search cases by clue match
        response = self.client.get(url, {
            'entity_type': ClueEntityType.PHONE_NUMBER,
            'value': '+918888877777'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['entity_type'], ClueEntityType.PHONE_NUMBER)
        self.assertEqual(response.data['data']['value'], '+918888877777')
        
        matching = response.data['data']['matching_cases']
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]['fir_number'], 'FIR/2026/00001')
