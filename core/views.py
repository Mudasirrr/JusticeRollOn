from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from .models import Evidence, Petition, ConsultationSlot, Deposition
from .serializers import (
    PetitionListSerializer,
    PetitionCreateSerializer,
    EvidenceSerializer,
    RegisterSerializer,
)

from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q


def home(request):
    return render(request, "home.html")

def register_page(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        role = request.POST.get("role", "citizen")
        from .models import User
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})
        u = User.objects.create_user(username=username, password=password, role=role)
        login(request, u)
        return redirect("dashboard")
    return render(request, "register.html")

def login_page(request):
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
    """
    Logs out the current user and redirects to login page.
    """
    logout(request)
    return redirect("login")

@login_required
def evidence_list(request):
    evidences = Evidence.objects.filter(uploader=request.user)
    return render(request, "evidence_list.html", {"evidences": evidences})

@login_required
def petition_list(request):
    """
    List petitions created by the current user with evidence and category info.
    """
    from .models import Petition, Evidence

    petitions = Petition.objects.filter(creator=request.user).prefetch_related("evidences")
    evidences = Evidence.objects.filter(uploader=request.user)

    # Define these choices manually since they're not in the model
    categories = [
        ("General", "General"),
        ("Legal Rights", "Legal Rights"),
        ("Public Welfare", "Public Welfare"),
        ("Environmental", "Environmental"),
        ("Policy Reform", "Policy Reform"),
    ]

    visibilities = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    return render(
        request,
        "petition_list.html",
        {
            "petitions": petitions,
            "evidences": evidences,
            "categories": categories,
            "visibilities": visibilities,
        },
    )


@login_required
def consultation_list(request):
    slots = ConsultationSlot.objects.filter(lawyer=request.user) if request.user.role == "lawyer" else ConsultationSlot.objects.all()
    return render(request, "consultation_list.html", {"slots": slots})

@login_required
def deposition_list(request):
    deps = Deposition.objects.filter(created_by=request.user)
    return render(request, "deposition_list.html", {"depositions": deps})

@login_required
def dashboard(request):
    if request.user.role == "admin":
        petitions = Petition.objects.filter(status="pending")
        return render(request, "dashboard.html", {"admin_view": True, "petitions": petitions})

    if request.user.role == "lawyer":
        slots = ConsultationSlot.objects.filter(lawyer=request.user)
        return render(request, "dashboard.html", {"lawyer_view": True, "slots": slots})

    evidences = Evidence.objects.filter(uploader=request.user)
    petitions = Petition.objects.filter(creator=request.user)
    return render(request, "dashboard.html", {"citizen_view": True, "evidences": evidences, "petitions": petitions})
   
@login_required
def dashboard2(request):
    if request.user.role == "admin":
        petitions = Petition.objects.filter(status="pending")
        return render(request, "dash.html", {"admin_view": True, "petitions": petitions})

    if request.user.role == "lawyer":
        slots = ConsultationSlot.objects.filter(lawyer=request.user)
        return render(request, "dash.html", {"lawyer_view": True, "slots": slots})

    evidences = Evidence.objects.filter(uploader=request.user)
    petitions = Petition.objects.filter(creator=request.user)
    return render(request, "dash.html", {"citizen_view": True, "evidences": evidences, "petitions": petitions})

def justice_index(request):
    """
    Public page showing all approved/published petitions.
    """
    query = request.GET.get("q", "").strip()
    petitions = Petition.objects.filter(status="published").order_by("-created_at")

    if query:
        petitions = petitions.filter(
            Q(title__icontains=query) | Q(category__icontains=query)
        )

    return render(request, "justice_index.html", {
        "petitions": petitions,
        "query": query,
    })

class PetitionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Petition CRUD and listing.
    Citizens can view their own petitions.
    Admin can view all.
    Public can view published ones.
    """
    queryset = Petition.objects.all().select_related("creator")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        # Use different serializer for create vs list/detail
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
            return Petition.objects.filter(creator=user)
        else:
            return Petition.objects.filter(status="published", visibility="public")

class EvidenceUploadAPI(generics.CreateAPIView):
    serializer_class = EvidenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


class RegisterAPI(generics.CreateAPIView):
    """
    Simple API endpoint for user registration (Citizen/Lawyer/Admin)
    """
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
    """
    Citizens can support a petition (join).
    """
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    # Simple rule: only citizens can join petitions
    if user.role != "citizen":
        return Response({"error": "Only citizens can support petitions."}, status=403)

    # Add the user to supporters if not already
    if petition.supporters.filter(id=user.id).exists():
        return Response({"message": "You already supported this petition."})
    else:
        petition.supporters.add(user)
        petition.supporter_count = petition.supporters.count()
        petition.save()
        return Response(
            {"message": "You supported this petition!", "supporters": petition.supporter_count},
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def approve_petition(request, pk):
    """
    Admins approve submitted petitions.
    """
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    if user.role != "admin":
        return Response({"error": "Only admins can approve petitions."}, status=403)

    petition.status = "published"
    petition.save()

    # ✅ For AJAX: return JSON only
    return Response(
        {"message": f"✅ Petition '{petition.title}' approved successfully!"},
        status=200
    )

# @login_required
# @csrf_exempt
# def petition_create(request):
#     """
#     Citizens can create new petitions.
#     """
#     if request.user.role != "citizen":
#         messages.warning(request, "Only citizens can create petitions.")
#         return redirect("dashboard")

#     if request.method == "POST":
#         title = request.POST.get("title")
#         description = request.POST.get("description")
#         category = request.POST.get("category", "General")
#         visibility = request.POST.get("visibility", "public")

#         if not title or not description:
#             messages.warning(request, "Please fill in all required fields.")
#             return redirect("petition_create")

#         Petition.objects.create(
#             title=title,
#             description=description,
#             category=category,
#             visibility=visibility,
#             creator=request.user,
#             status="pending"
#         )
#         messages.success(request, "Petition created successfully! Awaiting admin approval.")
#         return redirect("petition_list")

#     return render(request, "petition_create.html")

# core/views.py

@login_required
@csrf_exempt
def petition_create(request):
    """
    Citizens can create new petitions and attach uploaded evidence.
    """
    if request.user.role != "citizen":
        messages.warning(request, "Only citizens can create petitions.")
        return redirect("dashboard")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        category = request.POST.get("category", "General")
        visibility = request.POST.get("visibility", "public")
        evidence_ids = request.POST.getlist("evidences")

        if not title or not description:
            messages.warning(request, "Please fill in all required fields.")
            return redirect("petition_create")

        petition = Petition.objects.create(
            title=title,
            description=description,
            category=category,
            visibility=visibility,
            creator=request.user,
            status="draft",
        )

        # 🧩 Attach selected evidences
        if evidence_ids:
            petition.evidences.set(Evidence.objects.filter(id__in=evidence_ids))

        messages.success(request, "✅ Petition created successfully! Awaiting admin review.")
        return redirect("dashboard2")

    # 🖋️ Render form
    evidences = Evidence.objects.filter(uploader=request.user)
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
        {"evidences": evidences, "categories": categories},
    )


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def submit_for_review(request, pk):
    """
    Citizens can submit their petition for admin review.
    """
    petition = get_object_or_404(Petition, pk=pk)
    user = request.user

    # ✅ Only the petition creator can submit it
    if petition.creator != user:
        return Response(
            {"error": "You can only submit your own petitions."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # ✅ Only citizens can submit
    if user.role != "citizen":
        return Response(
            {"error": "Only citizens can submit petitions for review."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # ✅ Prevent duplicate submissions
    if petition.status != "draft":
        return Response(
            {"message": f"This petition is already {petition.status}."},
            status=status.HTTP_200_OK,
        )

    petition.status = "pending"
    petition.save()
    return Response(
        {"message": f"✅ Petition '{petition.title}' submitted for admin review."},
        status=status.HTTP_200_OK,
    )


def petition_detail(request, pk):
    """
    Public petition detail view — shows full petition info.
    Citizens can also support a petition here.
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

