# from django.urls import path, include
# from . import views
# from rest_framework.routers import DefaultRouter
# from .views import PetitionViewSet, RegisterAPI, EvidenceUploadAPI, join_petition, submit_for_review, approve_petition

# router = DefaultRouter()
# router.register(r"petitions", PetitionViewSet, basename="petition")

# urlpatterns = [
#     path("", views.home, name="home"),
#     path("register/", views.register_page, name="register"),
#     path("login/", views.login_page, name="login"),
#     path("dashboard/", views.dashboard, name="dashboard"),
#     path("justice-index/", views.justice_index, name="justice_index"),
#     path("petition/<int:pid>/", views.petition_detail, name="petition_detail"),
#     path("deposition-builder/", views.deposition_builder, name="deposition_builder"),

#     # APIs
#     path("api/register/", RegisterAPI.as_view(), name="api-register"),
#     path("api/upload-evidence/", EvidenceUploadAPI.as_view(), name="api-upload-evidence"),
#     path("api/", include(router.urls)),
#     path("api/petition/<int:pk>/join/", join_petition, name="api-join-petition"),
#     path("api/petition/<int:pk>/submit-for-review/", submit_for_review, name="api-submit-petition"),
#     path("api/petition/<int:pk>/approve/", approve_petition, name="api-approve-petition"),
# ]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    PetitionViewSet,
    RegisterAPI,
    EvidenceUploadAPI,
    join_petition,
    approve_petition,
    submit_for_review,
    petition_detail,     # ✅ add this line
    justice_index,
)

router = DefaultRouter()
router.register(r"petitions", PetitionViewSet, basename="petition")

urlpatterns = [
    # --- Web pages ---
    path("", views.home, name="home"),
    path("register/", views.register_page, name="register"),
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("justice-index/", views.justice_index, name="justice_index"),
    path("evidences/", views.evidence_list, name="evidence_list"),
    path("petitions/", views.petition_list, name="petition_list"),
    path("petitions/create/", views.petition_create, name="petition_create"),
    path("petitions/<int:pk>/", petition_detail, name="petition_detail"),
    path("dashboard2/", views.dashboard2, name="dashboard2"),

    # --- REST API ---
    path("api/register/", RegisterAPI.as_view(), name="api-register"),
    path("api/upload-evidence/", EvidenceUploadAPI.as_view(), name="api-upload-evidence"),
    path("api/petition/<int:pk>/join/", join_petition, name="api-join-petition"),
    path("api/petition/<int:pk>/approve/", approve_petition, name="api-approve-petition"),
    path("api/petition/<int:pk>/submit-for-review/", submit_for_review, name="api-submit-for-review"),

    path("api/", include(router.urls)),
]



