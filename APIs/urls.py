from django.urls import path
from .views import (
    get_members,
    EmailTokenObtainPairView,
    activate_trainee,
    get_pending_registrations,
)

app_name = "apis"

urlpatterns = [
    # Auth
    path(
        "auth/login/",
        EmailTokenObtainPairView.as_view(),
        name="login",
    ),

    # Members
    path(
        "members/",
        get_members,
        name="member_info",
    ),

    # Trainee
    path(
        "trainee/activate/",
        activate_trainee,
        name="activate_trainee",
    ),
    path(
        "pending-trainees/",
        get_pending_registrations,
        name="pending_trainees",
    ),
]