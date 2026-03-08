import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classbridge.settings')
django.setup()

from django.template.loader import render_to_string
from core.models import CustomUser

user = CustomUser.objects.filter(user_type='coordinator').first()
if user:
    context = {'coordinator_profile': user.coordinator_profile}
    html = render_to_string('dashboard_coordinator.html', context)
    with open('real_output.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Rendered and saved to real_output.html")
else:
    print("No coordinator found")
