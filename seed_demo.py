"""
see_demo.py

A standalone script to seed the Django database with demo data for development
and testing purposes. This script creates sample users, petitions, evidence,
consultation slots, and depositions.

Usage:
    python see_demo.py

Note: Run this only in a development environment. It clears existing demo data
      (except superusers) and creates predictable test accounts.
"""

import os
import django
from django.utils import timezone
from random import choice
from datetime import timedelta

# Configure Django settings and initialize the Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "justice_rollon.settings")
django.setup()

# Import models after django.setup() to avoid AppRegistryNotReady errors
from core.models import User, Petition, Evidence, ConsultationSlot, Deposition


# =============================================================================
# CLEAR EXISTING DEMO DATA
# =============================================================================
print("🧹 Clearing old demo data...")

# Optional: Keep superusers intact (uncomment if needed)
# User.objects.exclude(is_superuser=True).delete()

# Delete all existing records from relevant models to ensure clean, repeatable runs
Petition.objects.all().delete()
Evidence.objects.all().delete()
ConsultationSlot.objects.all().delete()
Deposition.objects.all().delete()

print("Old data cleared.\n")


# =============================================================================
# CREATE USERS
# =============================================================================
print("👥 Creating demo users...")

# Admin user (superuser with full access)
admin, _ = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@test.com",
        "role": "admin",
        "is_superuser": True,
        "is_staff": True,
    },
)
admin.set_password("admin123")  # Set a known password
admin.save()

# Lawyer user
lawyer, _ = User.objects.get_or_create(
    username="lawyer1",
    defaults={"email": "lawyer@test.com", "role": "lawyer"},
)
lawyer.set_password("lawyer123")
lawyer.save()

# Citizen users (regular petitioners)
citizen1, _ = User.objects.get_or_create(
    username="citizen1",
    defaults={"email": "citizen1@test.com", "role": "citizen"},
)
citizen1.set_password("citizen123")
citizen1.save()

citizen2, _ = User.objects.get_or_create(
    username="citizen2",
    defaults={"email": "citizen2@test.com", "role": "citizen"},
)
citizen2.set_password("citizen123")
citizen2.save()

print("Users ready:")
print(f" - Admin: {admin.username}")
print(f" - Lawyer: {lawyer.username}")
print(f" - Citizens: {citizen1.username}, {citizen2.username}\n")


# =============================================================================
# CREATE PETITIONS
# =============================================================================
print("📜 Creating sample petitions...")

p1 = Petition.objects.create(
    title="Clean Water for All",
    description="Request for ensuring clean water supply in rural areas.",
    category="Environment",
    creator=citizen1,
    visibility="public",
    status="pending",  # Still under review
)

p2 = Petition.objects.create(
    title="Better Road Safety",
    description="Petition to improve road lighting and traffic management.",
    category="Infrastructure",
    creator=citizen2,
    visibility="public",
    status="published",
    published_at=timezone.now(),  # Already live
)

print(f"Petitions added: {Petition.objects.count()}\n")


# =============================================================================
# UPLOAD EVIDENCE
# =============================================================================
print("📁 Adding evidence files...")

Evidence.objects.create(
    title="Water Quality Report",
    file_type="pdf",
    file="uploads/evidence/water_report.pdf",
    uploader=citizen1,
    verification_status="verified",
    size_bytes=12345,
)

Evidence.objects.create(
    title="Road Accident Statistics",
    file_type="csv",
    file="uploads/evidence/accident_stats.csv",
    uploader=citizen2,
    verification_status="pending",
    size_bytes=23456,
)

print(f"Evidences added: {Evidence.objects.count()}\n")


# =============================================================================
# CREATE CONSULTATION SLOTS
# =============================================================================
print("📅 Creating available consultation slots for the lawyer...")

# Create 3 slots on consecutive days starting tomorrow
for i in range(3):
    ConsultationSlot.objects.create(
        lawyer=lawyer,
        start_time=timezone.now() + timedelta(days=i + 1, hours=10 + i),
        duration_minutes=30,
        is_booked=False,
    )

print(f"Consultation slots created: {ConsultationSlot.objects.count()}\n")


# =============================================================================
# CREATE DEPOSITIONS
# =============================================================================
print("🧾 Creating sample depositions...")

Deposition.objects.create(
    title="Clean Water Case Deposition",
    content="Detailed deposition prepared by lawyer for the water supply petition case.",
    created_by=lawyer,
    created_at=timezone.now(),
)

Deposition.objects.create(
    title="Road Safety Petition Report",
    content="Supporting statement and details for the road safety improvement petition.",
    created_by=citizen1,
    created_at=timezone.now(),
)

print(f"Depositions created: {Deposition.objects.count()}\n")


# =============================================================================
# FINAL SUCCESS MESSAGE & LOGIN INSTRUCTIONS
# =============================================================================
print("✅ DEMO DATA SEEDED SUCCESSFULLY!\n")

print("Test these login credentials:")
print(" - Admin       → username: admin     | password: admin123")
print(" - Lawyer      → username: lawyer1   | password: lawyer123")
print(" - Citizen 1   → username: citizen1  | password: citizen123")
print(" - Citizen 2   → username: citizen2  | password: citizen123")

print("\nNext steps:")
print(" - Start the server: python manage.py runserver")
print(" - Login at: http://127.0.0.1:8000/login/")
print(" - View petitions at: http://127.0.0.1:8000/justice-index/")
print("\nEnjoy testing the Justice RollOn platform! 🚀")