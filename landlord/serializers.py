from rest_framework import serializers
from .models import Property, Room


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'description', 'room_count']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'property', 'room_number',
                  'floor', 'type', 'rent', 'tenant']
        read_only_fields = ['tenant']
