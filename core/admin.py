from django.contrib import admin
from .models import (
    User, Evidence, Petition,
    ConsultationSlot, ConsultationBooking,
    Deposition, DepositionEvidence, AuditLog
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    list_display = ("username", "email", "role", "is_staff", "is_superuser")


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ("title", "uploader", "file_type", "uploaded_at", "verification_status", "rule_violation", "party_involved", "harm")
    list_filter = ("verification_status", "file_type")
    search_fields = ("title", "uploader__username")


@admin.register(Petition)
class PetitionAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "status", "supporter_count", "visibility", "created_at")
    list_filter = ("status", "visibility")
    search_fields = ("title", "creator__username")


@admin.register(ConsultationSlot)
class ConsultationSlotAdmin(admin.ModelAdmin):
    list_display = ("lawyer", "start_time", "duration_minutes", "is_booked")
    list_filter = ("lawyer", "is_booked")


@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    list_display = ("slot", "user", "confirmed", "created_at")
    list_filter = ("confirmed",)


@admin.register(Deposition)
class DepositionAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at", "updated_at")


@admin.register(DepositionEvidence)
class DepositionEvidenceAdmin(admin.ModelAdmin):
    list_display = ("deposition", "evidence", "order")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    search_fields = ("user__username", "action")
