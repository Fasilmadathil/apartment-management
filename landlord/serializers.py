from rest_framework import serializers
from .models import Property, Room, Payment, ElectricityBill, CommunityMessage, ChatMessage


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'description', 'room_count']


class LandlordInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = []

class PropertyInfoSerializer(serializers.ModelSerializer):
    landlord = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'description', 'landlord']

    def get_landlord(self, obj):
        user = obj.landlord
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

class RoomDetailTenantSerializer(serializers.ModelSerializer):
    property = PropertyInfoSerializer(read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_number', 'floor', 'type', 'rent', 'property']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'property', 'room_number',
                  'floor', 'type', 'rent', 'tenant']
        read_only_fields = ['tenant']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'screenshot', 'date', 'status']
        read_only_fields = ['date', 'status']

    def create(self, validated_data):
        # Automatically set tenant and room
        validated_data['tenant'] = self.context['request'].user
        validated_data['room'] = self.context['request'].user.rooms.first()
        return super().create(validated_data)

class PaymentListSerializer(serializers.ModelSerializer):
    tenant = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'tenant', 'room', 'amount', 'screenshot', 'date', 'status']

    def get_tenant(self, obj):
        return {
            'id': obj.tenant.id,
            'username': obj.tenant.username,
            'email': obj.tenant.email,
        }

    def get_room(self, obj):
        return {
            'id': obj.room.id,
            'room_number': obj.room.room_number,
            'property_name': obj.room.property.name,
        }


class AssignTenantSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    tenant_email = serializers.EmailField()


class ElectricityBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectricityBill
        fields = ['id', 'room', 'amount', 'month', 'is_paid', 'created_at']
        read_only_fields = ['is_paid', 'created_at']


class CommunityMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = CommunityMessage
        fields = ['id', 'sender', 'sender_name', 'title', 'content', 'created_at']
        read_only_fields = ['sender', 'created_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'message', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp', 'is_read']







