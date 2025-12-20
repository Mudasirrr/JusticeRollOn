"""
Admin configuration for the Justice RollOn core app.

Registers all models with the Django admin site and provides customized,
user-friendly list views, filters, search, and read-only protections where needed.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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
    """Custom admin for the extended User model with role support."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role & Permissions", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    list_editable = ("role",)  # Quick role changes from list view


# =============================================================================
# EVIDENCE ADMIN
# =============================================================================
@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """Admin interface for managing and moderating uploaded evidence."""
    list_display = (
        "title",
        "uploader",
        "file_type",
        "uploaded_at",
        "verification_status",
        "rule_violation",
        "party_involved",
    )
    list_filter = ("verification_status", "file_type", "uploaded_at", "rule_violation")
    search_fields = ("title", "uploader__username", "description")
    readonly_fields = ("uploaded_at", "size_bytes")
    date_hierarchy = "uploaded_at"


# =============================================================================
# PETITION ADMIN
# =============================================================================
@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    """Admin interface for reviewing and managing petitions."""
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
    """Admin view for lawyer consultation availability."""
    list_display = ("lawyer", "start_time", "end_time_display", "duration_minutes", "is_booked")
    list_filter = ("lawyer", "is_booked", "start_time")
    date_hierarchy = "start_time"

    def end_time_display(self, obj):
        """Show calculated end time in the list view."""
        return obj.end_time if hasattr(obj, "end_time") else "-"
    end_time_display.short_description = "End Time"


# =============================================================================
# CONSULTATION BOOKING ADMIN
# =============================================================================
@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    """Admin interface for booked consultation slots."""
    list_display = ("slot", "user", "confirmed", "created_at")
    list_filter = ("confirmed", "slot__lawyer", "created_at")
    search_fields = ("user__username", "slot__lawyer__username")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


# =============================================================================
# DEPOSITION ADMIN
# =============================================================================
@admin.register(Deposition)
class DepositionAdmin(admin.ModelAdmin):
    """Admin interface for legal depositions."""
    list_display = ("title", "created_by", "created_at", "updated_at")
    list_filter = ("created_by", "created_at")
    search_fields = ("title", "content", "created_by__username")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


# =============================================================================
# DEPOSITION EVIDENCE (THROUGH MODEL) ADMIN
# =============================================================================
@admin.register(DepositionEvidence)
class DepositionEvidenceAdmin(admin.ModelAdmin):
    """Admin interface for ordering evidence within depositions."""
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
    Read-only admin view for audit logs.
    Only displays fields that actually exist on the model: user, action, timestamp, meta.
    """
    list_display = ("user", "action", "timestamp", "meta_preview")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "action")
    readonly_fields = ("user", "action", "timestamp", "meta")
    date_hierarchy = "timestamp"

    # Prevent any creation, modification, or deletion of audit logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    # Friendly preview of the JSON meta field
    def meta_preview(self, obj):
        if not obj.meta:
            return "-"
        import json
        try:
            pretty = json.dumps(obj.meta, indent=2, ensure_ascii=False)
            return pretty[:150] + ("..." if len(pretty) > 150 else "")
        except Exception:
            return str(obj.meta)[:150] + "..."
    meta_preview.short_description = "Meta Details"