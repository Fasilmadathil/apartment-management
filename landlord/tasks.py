from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import logging

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_payment_notification(self, payment_id):
    """Send email to landlord when tenant uploads a payment."""
    from .models import Payment

    try:
        payment = Payment.objects.select_related(
            'room__property__landlord', 'tenant'
        ).get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error(f"Payment {payment_id} not found, skipping notification.")
        return

    landlord = payment.room.property.landlord
    tenant = payment.tenant

    send_mail(
        subject=f'New Payment Uploaded - {payment.room.property.name}',
        message=(
            f'Tenant {tenant.username} uploaded a {payment.payment_type} '
            f'payment of ${payment.amount} for room {payment.room.room_number}.'
        ),
        from_email='noreply@apartment.com',
        recipient_list=[landlord.email],
        fail_silently=False,
    )
    logger.info(f"Payment notification sent for Payment#{payment_id}")


@shared_task(bind=True, max_retries=2, autoretry_for=(Exception,))
def generate_income_report(self, landlord_id):
    """Pre-compute and cache monthly income analytics for a landlord."""
    from .models import Payment
    from django.core.cache import cache

    payments = Payment.objects.filter(
        room__property__landlord_id=landlord_id,
        status='approved'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    data = [
        {'month': p['month'].strftime('%Y-%m'), 'total': str(p['total'])}
        for p in payments
    ]

    cache_key = f"income_report_{landlord_id}"
    cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
    logger.info(f"Income report cached for Landlord#{landlord_id}")
    return data


@shared_task(bind=True, max_retries=3, autoretry_for=(Exception,))
def generate_monthly_bills(self):
    """Periodic task: Generate electricity bill placeholders for all occupied rooms."""
    from .models import Room, ElectricityBill
    from django.utils import timezone

    first_of_month = timezone.now().replace(day=1).date()
    rooms = Room.objects.filter(tenant__isnull=False)

    created = 0
    for room in rooms:
        _, was_created = ElectricityBill.objects.get_or_create(
            room=room,
            month=first_of_month,
            defaults={'amount': 0, 'is_paid': False}
        )
        if was_created:
            created += 1

    logger.info(f"Generated {created} electricity bill placeholders for {first_of_month}")
    return created
