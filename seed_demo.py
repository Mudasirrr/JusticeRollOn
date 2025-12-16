import os
import django
from django.utils import timezone
from random import choice
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "justice_rollon.settings")
django.setup()

from core.models import User, Petition, Evidence, ConsultationSlot, Deposition

# Clear existing data (optional for repeatable runs)
# User.objects.exclude(is_superuser=True).delete()
Petition.objects.all().delete()
Evidence.objects.all().delete()
ConsultationSlot.objects.all().delete()
Deposition.objects.all().delete()

print("🧹 Old data cleared...")

# --- USERS ---
admin, _ = User.objects.get_or_create(
    username="admin",
    defaults={"email": "admin@test.com", "role": "admin", "is_superuser": True, "is_staff": True}
)
admin.set_password("admin123")
admin.save()

lawyer, _ = User.objects.get_or_create(
    username="lawyer1",
    defaults={"email": "lawyer@test.com", "role": "lawyer"}
)
lawyer.set_password("lawyer123")
lawyer.save()

citizen1, _ = User.objects.get_or_create(
    username="citizen1",
    defaults={"email": "citizen1@test.com", "role": "citizen"}
)
citizen1.set_password("citizen123")
citizen1.save()

citizen2, _ = User.objects.get_or_create(
    username="citizen2",
    defaults={"email": "citizen2@test.com", "role": "citizen"}
)
citizen2.set_password("citizen123")
citizen2.save()

print("👥 Users ready:")
print(f" - Admin: {admin.username}")
print(f" - Lawyer: {lawyer.username}")
print(f" - Citizens: {citizen1.username}, {citizen2.username}")


# --- PETITIONS ---
p1 = Petition.objects.create(
    title="Clean Water for All",
    description="Request for ensuring clean water supply in rural areas.",
    category="Environment",
    creator=citizen1,
    visibility="public",
    status="pending"
)
p2 = Petition.objects.create(
    title="Better Road Safety",
    description="Petition to improve road lighting and traffic management.",
    category="Infrastructure",
    creator=citizen2,
    visibility="public",
    status="published",
    published_at=timezone.now()
)

print("📜 Petitions added:", Petition.objects.count())

# --- EVIDENCES ---
Evidence.objects.create(
    title="Water report",
    file_type="pdf",
    file="uploads/evidence/water_report.pdf",
    uploader=citizen1,
    verification_status="verified",
    size_bytes=12345
)

Evidence.objects.create(
    title="Road accident stats",
    file_type="csv",
    file="uploads/evidence/accident_stats.csv",
    uploader=citizen2,
    verification_status="pending",
    size_bytes=23456
)

print("📁 Evidences added:", Evidence.objects.count())

# --- CONSULTATION SLOTS ---
for i in range(3):
    ConsultationSlot.objects.create(
        lawyer=lawyer,
        start_time=timezone.now() + timedelta(days=i + 1, hours=10 + i),
        duration_minutes=30,
        is_booked=False
    )

print("📅 Consultation slots created:", ConsultationSlot.objects.count())

# --- DEPOSITIONS ---
Deposition.objects.create(
    title="Clean Water Case",
    content="Deposition prepared for water supply case.",
    created_by=lawyer,
    created_at=timezone.now()
)
Deposition.objects.create(
    title="Accident Report",
    content="Details of road safety petition case.",
    created_by=citizen1,
    created_at=timezone.now()
)

print("🧾 Depositions created:", Deposition.objects.count())

print("\n✅ DEMO DATA SEEDED SUCCESSFULLY!")
print("Now test these logins:")
print(" - Admin: admin / admin123")
print(" - Lawyer: lawyer1 / lawyer123")
print(" - Citizen1: citizen1 / citizen123")
print(" - Citizen2: citizen2 / citizen123")

print("\n✅ Demo data seeded successfully! You can now:")
print(" - Login at http://127.0.0.1:8000/login/")
print(" - Explore petitions at http://127.0.0.1:8000/justice-index/")
