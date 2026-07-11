from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()

class UserAuthenticationTests(APITestCase):
    """
    Test suite verifying authentication operations and RBAC.
    """
    def setUp(self):
        self.supervisor = User.objects.create_user(
            username='supervisor_user',
            password='Password123!',
            role=UserRole.SUPERVISOR,
            badge_number='B-1111'
        )
        
        self.investigator = User.objects.create_user(
            username='investigator_user',
            password='Password123!',
            role=UserRole.INVESTIGATOR,
            badge_number='B-2222'
        )
        
        self.login_url = reverse('auth_login')
        self.me_url = reverse('users-me')

    def test_jwt_login_and_access_profile(self):
        # Attempt login
        response = self.client.post(self.login_url, {
            'username': 'investigator_user',
            'password': 'Password123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        access_token = response.data['access']
        
        # Request profile without token
        response_me_anon = self.client.get(self.me_url)
        self.assertEqual(response_me_anon.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Request profile with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response_me_auth = self.client.get(self.me_url)
        self.assertEqual(response_me_auth.status_code, status.HTTP_200_OK)
        self.assertEqual(response_me_auth.data['status'], 'success')
        self.assertEqual(response_me_auth.data['data']['username'], 'investigator_user')
        self.assertEqual(response_me_auth.data['data']['role'], UserRole.INVESTIGATOR)

    def test_rbac_user_list_restrictions(self):
        # Logged in as investigator
        self.client.force_authenticate(user=self.investigator)
        user_list_url = reverse('users-list')
        response = self.client.get(user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Logged in as supervisor
        self.client.force_authenticate(user=self.supervisor)
        response = self.client.get(user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
