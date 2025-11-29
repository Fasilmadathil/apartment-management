from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from superadmin.models import Role

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name='admin')
        self.tenant_role = Role.objects.create(name='tenant')
        
        self.register_url = '/register/'
        self.login_url = '/login/'

    def test_register_admin(self):
        data = {
            'username': 'newadmin',
            'email': 'admin@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newadmin').exists())
        user = User.objects.get(username='newadmin')
        self.assertEqual(user.role.name, 'admin') # Note: Serializer might capitalize or look for 'Admin'

    def test_login(self):
        user = User.objects.create_user(
            username='testuser',
            password='password123',
            role=self.tenant_role
        )
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
