from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from superadmin.models import Role
from .models import Property, Room, RoomType, Payment, ElectricityBill, CommunityMessage

User = get_user_model()

class LandlordTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name='admin')
        self.tenant_role = Role.objects.create(name='tenant')

        # Create Landlord
        self.landlord = User.objects.create_user(
            username='landlord1', password='password123', role=self.admin_role, email='landlord@test.com')
        
        # Create Tenant
        self.tenant = User.objects.create_user(
            username='tenant1', password='password123', role=self.tenant_role, email='tenant@test.com')

        # Authenticate as Landlord
        self.client.force_authenticate(user=self.landlord)

        # Setup Data
        self.property = Property.objects.create(
            name="Test Property", address="123 St", landlord=self.landlord, room_count=10)
        self.room_type = RoomType.objects.create(name="1BHK")
        self.room = Room.objects.create(
            property=self.property, room_number="101", floor=1, type=self.room_type, rent=1000.00)

    def test_create_property(self):
        data = {
            'name': 'New Property',
            'address': '456 Ave',
            'room_count': 5
        }
        response = self.client.post('/landlord/properties/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Property.objects.count(), 2)

    def test_assign_tenant(self):
        data = {
            'room_id': self.room.id,
            'tenant_email': self.tenant.email
        }
        response = self.client.post('/landlord/assign-tenant/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.tenant, self.tenant)

    def test_post_electricity_bill(self):
        data = {
            'room': self.room.id,
            'amount': 150.00,
            'month': '2023-11-01'
        }
        response = self.client.post('/landlord/electricity/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_community_message(self):
        data = {
            'title': 'Meeting',
            'content': 'Sunday 10AM'
        }
        response = self.client.post('/landlord/community/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_chat_flow(self):
        # Landlord sends message to Tenant
        data = {
            'receiver': self.tenant.id,
            'message': 'Hello Tenant'
        }
        response = self.client.post('/landlord/chat/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify message exists
        response = self.client.get('/landlord/chat/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['message'], 'Hello Tenant')

    def test_income_analytics(self):
        # Create a payment
        Payment.objects.create(
            room=self.room,
            tenant=self.tenant,
            amount=1000.00,
            payment_type='rent',
            status='approved',
            date='2023-11-01'
        )
        
        response = self.client.get('/landlord/analytics/income/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if data is returned (format: [{'month': 'YYYY-MM', 'total': 1000.00}])
        self.assertTrue(len(response.data) > 0)
        self.assertEqual(float(response.data[0]['total']), 1000.00)



class TenantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name='admin')
        self.tenant_role = Role.objects.create(name='tenant')

        self.landlord = User.objects.create_user(
            username='landlord1', password='password123', role=self.admin_role)
        self.tenant = User.objects.create_user(
            username='tenant1', password='password123', role=self.tenant_role)
        
        self.property = Property.objects.create(
            name="Test Property", address="123 St", landlord=self.landlord)
        self.room = Room.objects.create(
            property=self.property, room_number="101", floor=1, rent=1000.00, tenant=self.tenant)

        self.client.force_authenticate(user=self.tenant)

    def test_view_room_details(self):
        response = self.client.get('/landlord/tenant/room/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['room_number'], '101')

    def test_pay_rent(self):
        # Note: Image upload might need mock, but basic post check:
        data = {
            'amount': 1000.00,
            'payment_type': 'rent'
        }
        response = self.client.post('/landlord/tenant/payments/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().tenant, self.tenant)

    def test_view_landlord_contact(self):
        response = self.client.get('/landlord/tenant/contact/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.landlord.username)
