#!/usr/bin/env python
"""
Google OAuth sozlash uchun script
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Site ni yangilash
site = Site.objects.get(id=1)
site.domain = '127.0.0.1:8000'
site.name = 'Moliyaviy Boshqaruv'
site.save()
print(f"✅ Site yangilandi: {site.domain}")

# Google Social App yaratish yoki yangilash
google_app, created = SocialApp.objects.get_or_create(
    provider='google',
    defaults={
        'name': 'Google',
        'client_id': '',
        'secret': '',
    }
)

if not created:
    google_app.name = 'Google'
    google_app.client_id = ''
    google_app.secret = ''
    google_app.save()
    print("✅ Google Social App yangilandi")
else:
    print("✅ Google Social App yaratildi")

# Site ni qo'shish
google_app.sites.add(site)
print(f"✅ Site '{site.domain}' Google App ga qo'shildi")

print("\n🎉 Google OAuth muvaffaqiyatli sozlandi!")
print("Endi http://127.0.0.1:8000/login ga o'ting va 'Google bilan kirish' tugmasini bosing")
