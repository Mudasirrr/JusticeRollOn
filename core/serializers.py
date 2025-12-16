from rest_framework import serializers
from .models import User, Evidence, Petition, ConsultationSlot, ConsultationBooking, Deposition

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id","username","email","role")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ("username","email","password","role")
    def create(self, validated_data):
        u = User(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            role=validated_data.get("role", "citizen"),
        )
        u.set_password(validated_data["password"])
        u.save()
        return u

class EvidenceSerializer(serializers.ModelSerializer):
    uploader = UserSerializer(read_only=True)
    class Meta:
        model = Evidence
        fields = "__all__"
        read_only_fields = ("uploader","uploaded_at","size_bytes")

class PetitionSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    evidences = EvidenceSerializer(many=True, read_only=True)
    class Meta:
        model = Petition
        fields = "__all__"
        read_only_fields = ("creator","supporter_count","created_at","published_at","status")

class PetitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Petition
        fields = ("title","description","category","visibility")

class ConsultationSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationSlot
        fields = "__all__"

class ConsultationBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationBooking
        fields = "__all__"

class DepositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deposition
        fields = "__all__"

class PetitionListSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    evidences = EvidenceSerializer(many=True, read_only=True)

    class Meta:
        model = Petition
        fields = ("id", "title", "description", "category", "visibility", "status", "creator", "supporter_count", "evidences")
