from django.shortcuts import render
from django.db.models.signals import post_save
from django.dispatch import receiver
from superadmin.models import User
from .models import LandlordProfile
from rest_framework import generics, permissions
from .serializers import PropertySerializer, RoomSerializer
from .models import Property, Room
from rest_framework.exceptions import PermissionDenied
from .permissions import IsLandlord


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
