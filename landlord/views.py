from django.shortcuts import render
from django.db import models # Import models for Q objects
from django.dispatch import receiver
from django.db.models.signals import post_save
from superadmin.models import User
from .models import LandlordProfile
from rest_framework import generics, permissions
from .serializers import PropertySerializer, RoomSerializer, RoomDetailTenantSerializer, PaymentSerializer, PaymentListSerializer, AssignTenantSerializer, ElectricityBillSerializer, CommunityMessageSerializer, ChatMessageSerializer
from .models import Property, Room, Payment, ElectricityBill, CommunityMessage, ChatMessage
from rest_framework.exceptions import PermissionDenied
from .permissions import IsLandlord, IsTenant
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView





class PropertyListCreateView(generics.ListCreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Property.objects.filter(landlord=self.request.user)

    def perform_create(self, serializer):
        serializer.save(landlord=self.request.user)


class PropertyRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Property.objects.filter(landlord=self.request.user)


class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Room.objects.filter(property__landlord=self.request.user)

    def perform_create(self, serializer):
        prop = serializer.validated_data['property']
        if prop.landlord != self.request.user:
            raise PermissionDenied(
                "You can only add rooms to your own properties.")
        serializer.save()


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Room.objects.filter(property__landlord=self.request.user)


class TenantRoomDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTenant]

    def get(self, request):
        user = request.user
        room = user.rooms.first()
        if not room:
            return Response({'detail': 'No room assigned.'}, status=404)
        serializer = RoomDetailTenantSerializer(room)
        return Response(serializer.data)


class TenantPaymentCreateView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsTenant]

    def perform_create(self, serializer):
        serializer.save()

class TenantPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsTenant]

    def get_queryset(self):
        return Payment.objects.filter(tenant=self.request.user).order_by('-date')

class LandlordPaymentListView(generics.ListAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Payment.objects.filter(room__property__landlord=self.request.user).order_by('-date')

class LandlordPaymentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PaymentListSerializer
    permission_classes = [IsAuthenticated, IsLandlord]

    def get_queryset(self):
        return Payment.objects.filter(room__property__landlord=self.request.user)

    def patch(self, request, *args, **kwargs):
        payment = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in ['approved', 'rejected']:
            payment.status = new_status
            payment.save()
            return Response({'detail': f'Payment {new_status} successfully.'})
        
        return Response({'detail': 'Invalid status.'}, status=400)


class AssignTenantView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def post(self, request):
        serializer = AssignTenantSerializer(data=request.data)
        if serializer.is_valid():
            room_id = serializer.validated_data['room_id']
            tenant_email = serializer.validated_data['tenant_email']

            try:
                room = Room.objects.get(id=room_id, property__landlord=request.user)
            except Room.DoesNotExist:
                return Response({'detail': 'Room not found or does not belong to you.'}, status=404)

            try:
                tenant = User.objects.get(email=tenant_email)
                # Optional: Check if user is actually a tenant role
                # if tenant.role.name != 'tenant':
                #     return Response({'detail': 'User is not a tenant.'}, status=400)
            except User.DoesNotExist:
                return Response({'detail': 'Tenant not found.'}, status=404)

            room.tenant = tenant
            room.save()
            return Response({'detail': f'Tenant {tenant.username} assigned to room {room.room_number}.'})
        
        return Response(serializer.errors, status=400)


class ElectricityBillCreateView(generics.CreateAPIView):
    serializer_class = ElectricityBillSerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def perform_create(self, serializer):
        # Ensure the room belongs to the landlord
        room = serializer.validated_data['room']
        if room.property.landlord != self.request.user:
            raise PermissionDenied("You can only add bills for your own properties.")
        serializer.save()


class TenantElectricityBillListView(generics.ListAPIView):
    serializer_class = ElectricityBillSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenant]

    def get_queryset(self):
        # Show bills for the tenant's assigned room
        return ElectricityBill.objects.filter(room__tenant=self.request.user).order_by('-month')


class CommunityMessageCreateView(generics.CreateAPIView):
    serializer_class = CommunityMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class CommunityMessageListView(generics.ListAPIView):
    serializer_class = CommunityMessageSerializer
    permission_classes = [permissions.IsAuthenticated] # Both can view

    def get_queryset(self):
        return CommunityMessage.objects.all().order_by('-created_at')


class LandlordContactView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTenant]

    def get(self, request):
        user = request.user
        room = user.rooms.first()
        if not room:
            return Response({'detail': 'No room assigned.'}, status=404)
        
        landlord = room.property.landlord
        return Response({
            'name': landlord.username,
            'email': landlord.email,
            # Add phone number if available in profile
        })


class ChatView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get messages where user is sender OR receiver
        return ChatMessage.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        ).order_by('timestamp')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class IncomeAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsLandlord]

    def get(self, request):
        from django.db.models import Sum
        from django.db.models.functions import TruncMonth

        # Aggregate payments by month for the landlord's properties
        payments = Payment.objects.filter(
            room__property__landlord=request.user,
            status='approved'
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        data = [
            {
                'month': p['month'].strftime('%Y-%m'),
                'total': p['total']
            }
            for p in payments
        ]
        return Response(data)



