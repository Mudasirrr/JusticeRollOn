"""
core/serializers.py

Serializers for the Justice RollOn API.

These serializers convert complex Django model instances to and from native
Python datatypes (e.g., JSON) for use in Django REST Framework views.

They define:
- Which fields are exposed in the API
- Read-only vs. writable fields
- Nested representations (e.g., creator details, attached evidence)
- Custom creation logic (e.g., user registration with password hashing)

Best practices followed:
- Separation of read/list and create/update serializers where needed
- Proper use of read_only_fields for security
- Nested serializers for rich, usable responses
"""

from rest_framework import serializers

from .models import (
    User,
    Evidence,
    Petition,
    ConsultationSlot,
    ConsultationBooking,
    Deposition,
)


# =============================================================================
# USER SERIALIZERS
# =============================================================================
class UserSerializer(serializers.ModelSerializer):
    """
    Basic serializer for User model.
    Used for displaying user information (e.g., creator/uploader) in nested contexts.
    Does not expose passwords or sensitive fields.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")
        read_only_fields = fields  # All fields are read-only in this context


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration endpoint.
    Handles password hashing and sets default role if not provided.
    Password is write-only for security.
    """
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ("username", "email", "password", "role")
        extra_kwargs = {
            "email": {"required": False, "allow_blank": True},
            "role": {"required": False},
        }

    def create(self, validated_data):
        """Create a new user with hashed password and default role."""
        user = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            role=validated_data.get("role", "citizen"),  # Default to citizen
        )
        user.set_password(validated_data["password"])  # Properly hash password
        user.save()
        return user


# =============================================================================
# EVIDENCE SERIALIZER
# =============================================================================
class EvidenceSerializer(serializers.ModelSerializer):
    """
    Serializer for Evidence model.
    Includes nested uploader details for better frontend display.
    Prevents modification of uploader, upload time, and file size.
    """
    uploader = UserSerializer(read_only=True)

    class Meta:
        model = Evidence
        fields = "__all__"
        read_only_fields = ("uploader", "uploaded_at", "size_bytes", "verification_status")


# =============================================================================
# PETITION SERIALIZERS
# =============================================================================
class PetitionListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for listing petitions.
    Includes nested creator and evidence details for rich display without extra queries.
    Used in list views to reduce API roundtrips.
    """
    creator = UserSerializer(read_only=True)
    evidences = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Petition
        fields = (
            "id",
            "title",
            "description",
            "category",
            "visibility",
            "status",
            "creator",
            "supporter_count",
            "evidences",
            "created_at",
        )


class PetitionSerializer(serializers.ModelSerializer):
    """
    Full serializer for detailed petition views (retrieve/update).
    Includes nested creator and evidences.
    Protects critical fields like status and supporter count.
    """
    creator = UserSerializer(read_only=True)
    evidences = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Petition
        fields = "__all__"
        read_only_fields = (
            "creator",
            "supporter_count",
            "created_at",
            "published_at",
            "status",  # Only admins should change status
        )


class PetitionCreateSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for creating new petitions.
    Only allows fields that citizens should control.
    Creator is automatically set from request.user in the view.
    """
    class Meta:
        model = Petition
        fields = ("title", "description", "category", "visibility")
        extra_kwargs = {
            "description": {"help_text": "Detailed explanation of the issue and desired change."},
        }

    def validate(self, data):
        """Optional: Add custom validation (e.g., minimum description length)."""
        if len(data.get("description", "").strip()) < 50:
            raise serializers.ValidationError("Description must be at least 50 characters.")
        return data


# =============================================================================
# CONSULTATION SERIALIZERS
# =============================================================================
class ConsultationSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for lawyer consultation time slots.
    Allows lawyers to create/update their availability.
    """
    class Meta:
        model = ConsultationSlot
        fields = "__all__"
        read_only_fields = ("is_booked",)  # Booking status updated via booking creation


class ConsultationBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for booking a consultation slot.
    Typically used by citizens to book available slots.
    """
    class Meta:
        model = ConsultationBooking
        fields = "__all__"
        read_only_fields = ("confirmed", "created_at")  # Confirmation by lawyer


# =============================================================================
# DEPOSITION SERIALIZER
# =============================================================================
class DepositionSerializer(serializers.ModelSerializer):
    """
    Serializer for legal depositions.
    Allows lawyers/citizens to create and update depositions.
    Note: Evidence ordering via through model may need a custom serializer if exposed.
    """
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Deposition
        fields = "__all__"
        read_only_fields = ("created_by", "created_at", "updated_at")