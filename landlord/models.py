from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from superadmin.models import User


class LandlordProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='landlord_profile')
    subscription_start = models.DateField()
    subscription_end = models.DateField()
    proof = models.FileField(
        upload_to='landlord_proofs/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Landlord Profile"


class Property(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True)
    room_count = models.PositiveIntegerField(default=0)

    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    def __str__(self):
        return self.name


class Room(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    floor = models.IntegerField()
    type = models.ForeignKey('RoomType', on_delete=models.SET_NULL, null=True)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    tenant = models.ForeignKey(User, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='rooms')

    def __str__(self):
        return f"{self.property.name} - Room {self.room_number}"


class RoomType(models.Model):
    name = models.CharField(max_length=50)  # e.g., "1BHK", "2BHK", "Studio"
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Complaint(models.Model):
    tenant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='complaints')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.title} - {self.tenant.username}"


class Document(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='documents')
    tenant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    tenant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='payments')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    screenshot = models.ImageField(
        upload_to='payment_screenshots/', blank=True, null=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.tenant.username} - {self.amount} - {self.status}"


@receiver(post_save, sender=Payment)
def notify_landlord_payment_uploaded(sender, instance, created, **kwargs):
    if created:
        # Get the landlord of the property
        landlord = instance.room.property.landlord
        tenant = instance.tenant
        
        # You can add email notification here
        # For now, we'll just print to console (replace with email/notification system)
        print(f"NOTIFICATION: Tenant {tenant.username} uploaded payment of ${instance.amount} for room {instance.room.room_number}")
        print(f"Landlord {landlord.username} should be notified")
        
        # TODO: Add email notification
        # from django.core.mail import send_mail
        # send_mail(
        #     f'New Payment Uploaded - {instance.room.property.name}',
        #     f'Tenant {tenant.username} uploaded payment of ${instance.amount} for room {instance.room.room_number}',
        #     'from@example.com',
        #     [landlord.email],
        #     fail_silently=False,
        # )
