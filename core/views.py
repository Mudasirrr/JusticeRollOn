"""
core/views.py

Contains all views for the Justice RollOn platform.

Includes:
- Traditional Django function-based views for HTML template rendering (user-facing pages)
- Django REST Framework API views for JSON endpoints (frontend or mobile consumption)
- Role-based access control using user.role
- Authentication flows (login, logout, register)
- Petition lifecycle management (create, submit, approve, support)

Views are organized into logical sections for maintainability.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response

from .models import User, Evidence, Petition, ConsultationSlot, Deposition
from .serializers import (
    PetitionListSerializer,
    PetitionCreateSerializer,
    EvidenceSerializer,
    RegisterSerializer,
)


# =============================================================================
# PUBLIC PAGES
# =============================================================================
def home(request):
    """Render the homepage (public landing page)."""
    return render(request, "home.html")


def justice_index(request):
    """
    Public index of all published petitions.
    Supports search by title or category.
    """
    query = request.GET.get("q", "").strip()
    petitions = Petition.objects.filter(status="published").order_by("-created_at")

    if query:
        petitions = petitions.filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )

    return render(
        request,
        "justice_index.html",
        {"petitions": petitions, "query": query},
    )


def petition_detail(request, pk):
    """
    Public detail view for a single published petition.
    Shows full description, evidence, and support status.
    """
    petition = get_object_or_404(Petition, pk=pk, status="published")
    user_supported = False

    if request.user.is_authenticated:
        user_supported = petition.supporters.filter(id=request.user.id).exists()

    return render(
        request,
        "petition_detail.html",
        {
            "petition": petition,
            "user_supported": user_supported,
        },
    )


# =============================================================================
# AUTHENTICATION VIEWS
# =============================================================================
def register_page(request):
    """
    Handle user registration (citizen, lawyer, or admin).
    Creates user and logs them in immediately.
    """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST.get("role", "citizen")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        user = User.objects.create_user(username=username, password=password, role=role)
        login(request, user)
        return redirect("dashboard2")

    return render(request, "register.html")


def login_page(request):
    """Standard login page with error handling."""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard2")
        else:
            return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    """Log out the current user and redirect to login."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# =============================================================================
# USER DASHBOARDS & LISTS
# =============================================================================
@login_required
def dashboard(request):
    """Legacy dashboard — kept for backward compatibility."""
    return _dashboard_logic(request, template="dashboard.html")


@login_required
def dashboard2(request):
    """Current main dashboard with role-based views."""
    return _dashboard_logic(request, template="dash.html")


def _dashboard_logic(request, template):
    """
    Shared logic for both dashboards.
    Displays different content based on user role.
    """
    if request.user.role == "admin":
        pending_petitions = Petition.objects.filter(status="pending")
        return render(request, template, {"admin_view": True, "petitions": pending_petitions})

    if request.user.role == "lawyer":
        slots = ConsultationSlot.objects.filter(lawyer=request.user)
        return render(request, template, {"lawyer_view": True, "slots": slots})

    # Citizen view
    evidences = Evidence.objects.filter(uploader=request.user)
    petitions = Petition.objects.filter(creator=request.user)
    return render(
        request,
        template,
        {"citizen_view": True, "evidences": evidences, "petitions": petitions},
    )


@login_required
def evidence_list(request):
    """List all evidence uploaded by the current user."""
    evidences = Evidence.objects.filter(uploader=request.user)
    return render(request, "evidence_list.html", {"evidences": evidences})


@login_required
def petition_list(request):
    """List petitions created by the current user."""
    petitions = Petition.objects.filter(creator=request.user).prefetch_related("evidences")
    user_evidences = Evidence.objects.filter(uploader=request.user)

    categories = [
        "General",
        "Legal Rights",
        "Public Welfare",
        "Environmental",
        "Policy Reform",
    ]

    visibilities = ["public", "private"]

    return render(
        request,
        "petition_list.html",
        {
            "petitions": petitions,
            "evidences": user_evidences,
            "categories": categories,
            "visibilities": visibilities,
        },
    )


@login_required
def consultation_list(request):
    """Lawyers see their slots; others see all available slots."""
    if request.user.role == "lawyer":
        slots = ConsultationSlot.objects.filter(lawyer=request.user)
    else:
        slots = ConsultationSlot.objects.filter(is_booked=False)

    return render(request, "consultation_list.html", {"slots": slots})


@login_required
def deposition_list(request):
    """List depositions created by the current user."""
    depositions = Deposition.objects.filter(created_by=request.user)
    return render(request, "deposition_list.html", {"depositions": depositions})


# =============================================================================
# PETITION CREATION
# =============================================================================
@login_required
@csrf_exempt  # Only if form uses AJAX/multipart; consider removing if not needed
def petition_create(request):
    """
    Allow citizens to create a new petition and attach their uploaded evidence.
    Status starts as 'draft'.
    """
    if request.user.role != "citizen":
        messages.warning(request, "Only citizens can create petitions.")
        return redirect("dashboard2")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category", "General")
        visibility = request.POST.get("visibility", "public")
        evidence_ids = request.POST.getlist("evidences")

        if not title or not description:
            messages.warning(request, "Title and description are required.")
            return redirect("petition_create")

        petition = Petition.objects.create(
            title=title,
            description=description,
            category=category,
            visibility=visibility,
            creator=request.user,
            status="draft",  # Starts as draft until submitted
        )

        # Attach selected evidence
        if evidence_ids:
            valid_evidences = Evidence.objects.filter(
                id__in=evidence_ids, uploader=request.user
            )
            petition.evidences.set(valid_evidences)

        messages.success(request, "Petition draft created successfully!")
        return redirect("dashboard2")

    # GET: Show creation form
    user_evidences = Evidence.objects.filter(uploader=request.user)
    categories = [
        "General",
        "Legal Rights",
        "Public Welfare",
        "Environmental",
        "Policy Reform",
    ]

    return render(
        request,
        "petition_create.html",
        {"evidences": user_evidences, "categories": categories},
    )


# =============================================================================
# API VIEWS (Django REST Framework)
# =============================================================================
class PetitionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and creating petitions.
    - Authenticated users: see their own + published public ones
    - Admins: see all
    - Anonymous: only published public petitions
    """
    queryset = Petition.objects.all().select_related("creator").prefetch_related("evidences")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PetitionListSerializer
        return PetitionCreateSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == "admin":
            return Petition.objects.all()
        elif user.is_authenticated:
            return Petition.objects.filter(
                Q(creator=user) | Q(status="published", visibility="public")
            )
        return Petition.objects.filter(status="published", visibility="public")


class EvidenceUploadAPI(generics.CreateAPIView):
    """API endpoint for uploading evidence files."""
    serializer_class = EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


class RegisterAPI(generics.CreateAPIView):
    """API endpoint for user registration (used by frontend apps)."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def join_petition(request, pk):
    """Allow citizens to support (join) a published petition."""
    petition = get_object_or_404(Petition, pk=pk, status="published")
    user = request.user

    if user.role != "citizen":
        return Response({"error": "Only citizens can support petitions."}, status=403)

    if petition.supporters.filter(id=user.id).exists():
        return Response({"message": "You already support this petition."})

    petition.supporters.add(user)
    petition.supporter_count = petition.supporters.count()
    petition.save(update_fields=["supporter_count"])

    return Response(
        {
            "message": "Thank you for your support!",
            "supporters": petition.supporter_count,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def approve_petition(request, pk):
    """Allow admins to approve a pending petition."""
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if user.role != "admin":
        return Response({"error": "Only admins can approve petitions."}, status=403)

    if petition.status != "pending":
        return Response({"message": "Petition is not pending review."})

    petition.status = "published"
    petition.published_at = timezone.now()
    petition.save()

    return Response(
        {"message": f"Petition '{petition.title}' has been approved and published!"},
        status=200,
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_for_review(request, pk):
    """Allow citizens to submit their draft petition for admin review."""
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if petition.creator != user:
        return Response({"error": "You can only submit your own petitions."}, status=403)

    if user.role != "citizen":
        return Response({"error": "Only citizens can submit petitions."}, status=403)

    if petition.status != "draft":
        return Response({"message": f"Petition is already {petition.status}."})

    petition.status = "pending"
    petition.save()

    return Response(
        {"message": f"Petition '{petition.title}' submitted for review."},
        status=200,
    )