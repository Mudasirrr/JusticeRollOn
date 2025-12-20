"""
Admin configuration for the justice_rollon project (core app).

This file registers models with the Django admin interface and customizes
how they are displayed, filtered, searched, and edited.

The Django admin provides a powerful, ready-to-use interface for managing
database content — ideal for superusers, moderators, and internal tools.

For more information:
https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Import all models from the current app (core.models)
from .models import (
    User,
    Evidence,
    Petition,
    ConsultationSlot,
    ConsultationBooking,
    Deposition,
    DepositionEvidence,
    AuditLog,
)


# =============================================================================
# CUSTOM USER ADMIN
# =============================================================================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for the custom User model.
    Extends Django's default UserAdmin to include the custom 'role' field.
    """

    # Add the 'role' field to the edit form (grouped under a "Role" section)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role & Permissions", {"fields": ("role",)}),
    )

    # Columns displayed in the user list view
    list_display = ("username", "email", "role", "is_staff", "is_superuser")

    # Optional: Make role editable directly from list view
    list_editable = ("role",)

    # Enable filtering by role in the right sidebar
    list_filter = ("role", "is_staff", "is_superuser", "is_active")

    # Enable search by username and email
    search_fields = ("username", "email")


# =============================================================================
# EVIDENCE ADMIN
# =============================================================================
@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """
    Admin interface for managing uploaded evidence files (PDFs, images, etc.).
    Useful for moderation and verification workflows.
    """

    list_display = (
        "title",
        "uploader",
        "file_type",
        "uploaded_at",
        "verification_status",
        "rule_violation",
        "party_involved",
        "harm",
    )
    list_filter = ("verification_status", "file_type", "uploaded_at", "rule_violation")
    search_fields = ("title", "uploader__username", "description")
    readonly_fields = ("uploaded_at", "size_bytes")  # Prevent accidental changes
    date_hierarchy = "uploaded_at"  # Quick date-based navigation


# =============================================================================
# PETITION ADMIN
# =============================================================================
@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing public petitions.
    Allows moderators to review, publish, or reject petitions.
    """

    list_display = (
        "title",
        "creator",
        "category",
        "status",
        "supporter_count",
        "visibility",
        "created_at",
        "published_at",
    )
    list_filter = ("status", "visibility", "category", "created_at")
    search_fields = ("title", "description", "creator__username")
    readonly_fields = ("supporter_count", "created_at", "published_at")
    date_hierarchy = "created_at"


# =============================================================================
# CONSULTATION SLOT ADMIN
# =============================================================================
@admin.register(ConsultationSlot)
class ConsultationSlotAdmin(admin.ModelAdmin):
    """
    Admin view for lawyer-available consultation time slots.
    Lawyers or admins can manage availability.
    """

    list_display = ("lawyer", "start_time", "end_time_display", "duration_minutes", "is_booked")
    list_filter = ("lawyer", "is_booked", "start_time")
    date_hierarchy = "start_time"

    def end_time_display(self, obj):
        """Display calculated end time for better readability."""
        return obj.end_time
    end_time_display.short_description = "End Time"


# =============================================================================
# CONSULTATION BOOKING ADMIN
# =============================================================================
@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    """
    Admin interface for booked consultations.
    Tracks which citizens have booked slots with lawyers.
    """

    list_display = ("slot", "user", "confirmed", "created_at", "notes")
    list_filter = ("confirmed", "slot__lawyer", "created_at")
    search_fields = ("user__username", "slot__lawyer__username")
    readonly_fields = ("created_at",)


# =============================================================================
# DEPOSITION ADMIN
# =============================================================================
@admin.register(Deposition)
class DepositionAdmin(admin.ModelAdmin):
    """
    Admin interface for legal depositions prepared by lawyers or citizens.
    """

    list_display = ("title", "created_by", "created_at", "updated_at")
    list_filter = ("created_by", "created_at")
    search_fields = ("title", "content", "created_by__username")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


# =============================================================================
# DEPOSITION EVIDENCE LINK ADMIN
# =============================================================================
@admin.register(DepositionEvidence)
class DepositionEvidenceAdmin(admin.ModelAdmin):
    """
    Admin interface for linking Evidence to Depositions (many-to-many with order).
    Controls the sequence of evidence presented in a deposition.
    """

    list_display = ("deposition", "evidence", "order")
    list_filter = ("deposition",)
    search_fields = ("deposition__title", "evidence__title")
    ordering = ("deposition", "order")


# =============================================================================
# AUDIT LOG ADMIN
# =============================================================================
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for system audit logs.
    Provides transparency into user actions (create, update, delete, etc.).
    Should be read-only to preserve integrity.
    """

    list_display = ("user", "action", "model_name", "object_id", "timestamp")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("user__username", "action", "details")
    readonly_fields = ("user", "action", "model_name", "object_id", "details", "timestamp")
    date_hierarchy = "timestamp"

    # Prevent any modifications to audit logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False