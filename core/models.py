"""
core/models.py

Defines the core data models for the Justice RollOn platform.

These models represent the main entities of the system:
- Users with roles (admin, lawyer, citizen)
- Evidence uploads with verification
- Public petitions with supporters
- Lawyer consultation scheduling
- Legal depositions with ordered evidence
- Audit logging for transparency

All models follow Django best practices and are designed for extensibility.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# =============================================================================
# CUSTOM USER MODEL
# =============================================================================
class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds a 'role' field to distinguish between admins, lawyers, and citizens.
    This replaces the default User model (configured in settings.py via AUTH_USER_MODEL).
    """

    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("lawyer", "Lawyer"),
        ("citizen", "Citizen"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="citizen",
        help_text="User role determining permissions and available features.",
    )

    def is_lawyer(self) -> bool:
        """Convenience method to check if user is a lawyer."""
        return self.role == "lawyer"

    def is_admin(self) -> bool:
        """Convenience method to check if user is an admin."""
        return self.role == "admin"

    def __str__(self) -> str:
        return self.username


# =============================================================================
# EVIDENCE MODEL
# =============================================================================
class Evidence(models.Model):
    """
    Represents uploaded supporting evidence (documents, images, videos, etc.)
    submitted by users to support petitions or depositions.
    Includes moderation fields for verification and rule compliance.
    """

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

    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="evidences",
        help_text="The user who uploaded this evidence.",
    )
    file = models.FileField(
        upload_to="evidence/",
        help_text="The actual uploaded file (stored in MEDIA_ROOT/evidence/).",
    )
    title = models.CharField(max_length=255, help_text="Descriptive title of the evidence.")
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default="other",
        help_text="Type of file for filtering and display purposes.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size_bytes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes (automatically populated on save).",
    )
    case_tag = models.CharField(
        max_length=128,
        blank=True,
        help_text="Optional tag to group evidence by case or topic.",
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default="pending",
        help_text="Moderation status: pending review, verified, or rejected.",
    )

    # Additional moderation/context fields
    rule_violation = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of any platform rule violation (if rejected).",
    )
    party_involved = models.CharField(
        max_length=255,
        blank=True,
        help_text="Names or entities involved in the evidence.",
    )
    harm = models.TextField(
        blank=True,
        help_text="Description of harm caused or alleged (for sensitive content review).",
    )

    def save(self, *args, **kwargs):
        """Automatically populate file size on save if file is attached."""
        if self.file:
            try:
                self.size_bytes = self.file.size
            except Exception:
                # In case file.size is not accessible (e.g., during migrations)
                pass
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.title} (by {self.uploader.username})"

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name_plural = "Evidence"


# =============================================================================
# PETITION MODEL
# =============================================================================
class Petition(models.Model):
    """
    Represents a public or private petition created by a citizen.
    Supports evidence attachment and community support via signatures.
    """

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="petitions",
        help_text="Citizen who created the petition.",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Full description of the petition.")
    category = models.CharField(
        max_length=100,
        choices=[
            ("general", "General"),
            ("legal", "Legal Rights"),
            ("welfare", "Public Welfare"),
            ("environment", "Environmental"),
            ("policy", "Policy Reform"),
        ],
        default="general",
    )
    visibility = models.CharField(
        max_length=20,
        choices=[("public", "Public"), ("private", "Private")],
        default="public",
        help_text="Private petitions are visible only to admins and creator.",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("pending", "Pending Review"),
            ("published", "Published"),
            ("rejected", "Rejected"),
        ],
        default="draft",
    )
    evidences = models.ManyToManyField(
        Evidence,
        related_name="petitions",
        blank=True,
        help_text="Supporting evidence attached to this petition.",
    )
    supporters = models.ManyToManyField(
        User,
        related_name="supported_petitions",
        blank=True,
        help_text="Users who have signed/supported this petition.",
    )
    supporter_count = models.PositiveIntegerField(
        default=0,
        help_text="Cached count of supporters for performance (updated via signals or save).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when petition was approved and made public.",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-created_at"]


# =============================================================================
# CONSULTATION SCHEDULING MODELS
# =============================================================================
class ConsultationSlot(models.Model):
    """
    Represents an available time slot offered by a lawyer for consultations.
    """

    lawyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "lawyer"},
        related_name="consultation_slots",
        help_text="Lawyer offering this consultation slot.",
    )
    start_time = models.DateTimeField(help_text="Start date and time of the slot.")
    duration_minutes = models.PositiveIntegerField(default=30)
    is_booked = models.BooleanField(default=False)

    @property
    def end_time(self):
        """Calculated end time for display purposes."""
        return self.start_time + timezone.timedelta(minutes=self.duration_minutes)

    def __str__(self) -> str:
        return f"{self.lawyer.get_full_name() or self.lawyer.username} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["start_time"]
        unique_together = ["lawyer", "start_time"]


class ConsultationBooking(models.Model):
    """
    Records a citizen booking a consultation slot.
    """

    slot = models.ForeignKey(
        ConsultationSlot,
        on_delete=models.CASCADE,
        related_name="bookings",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="consultation_bookings",
        help_text="Citizen who booked the consultation.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(
        default=False,
        help_text="Whether the lawyer has confirmed the booking.",
    )

    def __str__(self) -> str:
        return f"Booking by {self.user.username} for {self.slot}"

    class Meta:
        unique_together = ["slot", "user"]


# =============================================================================
# DEPOSITION MODELS
# =============================================================================
class Deposition(models.Model):
    """
    A legal deposition or compiled case narrative created by a lawyer or citizen.
    Can include multiple pieces of evidence in a specific order.
    """

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="depositions")
    title = models.CharField(max_length=255)
    content = models.TextField(
        blank=True,
        help_text="Compiled narrative, statement, or legal argument (supports HTML/plain text).",
    )
    evidences = models.ManyToManyField(
        Evidence,
        through="DepositionEvidence",
        blank=True,
        related_name="depositions",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} (by {self.created_by.username})"

    class Meta:
        ordering = ["-updated_at"]


class DepositionEvidence(models.Model):
    """
    Through model for ordered many-to-many relationship between Deposition and Evidence.
    Allows evidence to be presented in a specific sequence.
    """

    deposition = models.ForeignKey(Deposition, on_delete=models.CASCADE)
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, help_text="Display order in the deposition.")

    class Meta:
        ordering = ["order"]
        unique_together = ["deposition", "evidence"]

    def __str__(self) -> str:
        return f"{self.evidence.title} in {self.deposition.title}"


# =============================================================================
# AUDIT LOG MODEL
# =============================================================================
class AuditLog(models.Model):
    """
    Records important user actions for accountability and debugging.
    Should be populated via signals or service layers.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        help_text="User who performed the action (nullable if user deleted).",
    )
    action = models.CharField(max_length=255, help_text="Description of the action (e.g., 'created petition').")
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(
        blank=True,
        null=True,
        help_text="Additional context (e.g., object ID, IP address, request data).",
    )

    def __str__(self) -> str:
        username = self.user.username if self.user else "System"
        return f"[{self.timestamp}] {username}: {self.action}"

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action"]),
        ]