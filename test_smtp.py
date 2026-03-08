import os
import django
import sys

# Set up Django environment manually
sys.path.append('c:/DJANGO PROJECT/classbridge')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "classbridge.settings")
django.setup()

from django.core.mail import send_mail
from django.conf import settings

try:
    print(f"Testing SMTP with user: {settings.EMAIL_HOST_USER}")
    send_mail(
        'Test Subject',
        'Test Body.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"SMTP Error: {e}")
