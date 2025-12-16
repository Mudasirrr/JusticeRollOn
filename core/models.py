# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (("admin","Admin"), ("lawyer","Lawyer"), ("citizen","Citizen"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="citizen")

    def is_lawyer(self):
        return self.role == "lawyer"

    def is_admin(self):
        return self.role == "admin"

class Evidence(models.Model):
    FILE_TYPES = (
        ("image", "Image"),
        ("pdf", "PDF"),
        ("video", "Video"),
        ("doc", "Document"),
        ("other", "Other"),
    )

    VERIFICATION_STATUS = (
        ("pending", "Pending"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    )

    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evidences")
    file = models.FileField(upload_to="evidence/")
    title = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default="other")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size_bytes = models.PositiveIntegerField(null=True, blank=True)
    case_tag = models.CharField(max_length=128, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default="pending")

    # 🆕 New fields
    rule_violation = models.CharField(max_length=255, blank=True)
    party_involved = models.CharField(max_length=255, blank=True)
    harm = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.file:
            try:
                self.size_bytes = self.file.size
            except Exception:
                pass
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.uploader.username})"


class Petition(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="petitions")
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100, choices=[
        ("general", "General"),
        ("legal", "Legal Rights"),
        ("welfare", "Public Welfare"),
        ("environment", "Environmental"),
        ("policy", "Policy Reform"),
    ], default="general")
    visibility = models.CharField(max_length=20, choices=[("public", "Public"), ("private", "Private")], default="public")
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("published", "Published"),
            ("rejected", "Rejected"),
        ],
        default="draft",
    )
    evidences = models.ManyToManyField("Evidence", related_name="petitions", blank=True)
    supporters = models.ManyToManyField("User", related_name="supported_petitions", blank=True)  # ✅ add this
    supporter_count = models.PositiveIntegerField(default=0)  # ✅ optional, for fast counting
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class ConsultationSlot(models.Model):
    lawyer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role":"lawyer"})
    start_time = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.lawyer.username} - {self.start_time}"

class ConsultationBooking(models.Model):
    slot = models.ForeignKey(ConsultationSlot, on_delete=models.CASCADE, related_name="bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

class Deposition(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)  # compiled narrative (HTML or plain)
    evidences = models.ManyToManyField(Evidence, through="DepositionEvidence", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DepositionEvidence(models.Model):
    deposition = models.ForeignKey(Deposition, on_delete=models.CASCADE)
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(blank=True, null=True)
