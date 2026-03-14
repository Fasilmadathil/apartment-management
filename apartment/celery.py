import os
from celery import Celery

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apartment.settings')

app = Celery('apartment')

# Load config from Django settings, using CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()

# Worker reliability: re-queue tasks if worker crashes mid-execution
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_late = True

# Task routing: separate queues for different task types
app.conf.task_routes = {
    'landlord.tasks.send_payment_notification': {'queue': 'emails'},
    'landlord.tasks.generate_income_report': {'queue': 'analytics'},
    'landlord.tasks.generate_monthly_bills': {'queue': 'billing'},
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Simple debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
