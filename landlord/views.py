from django.shortcuts import render
from django.db.models.signals import post_save
from django.dispatch import receiver
from superadmin.models import User
from .models import LandlordProfile
from rest_framework import generics, permissions
from .serializers import PropertySerializer, RoomSerializer, RoomDetailTenantSerializer, PaymentSerializer, PaymentListSerializer
from .models import Property, Room, Payment
from rest_framework.exceptions import PermissionDenied
from .permissions import IsLandlord, IsTenant
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


@receiver(post_save, sender=User)
def create_landlord_profile(sender, instance, created, **kwargs):
    if created and instance.role.name == 'admin':
        LandlordProfile.objects.create(user=instance)


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
