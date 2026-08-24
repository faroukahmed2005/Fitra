from datetime import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest
from django.utils.decorators import method_decorator

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from firebase_admin import auth, firestore
from firebase_admin.auth import UserRecord

from django_ratelimit.decorators import ratelimit

from members.models import Member, PendingRegistration
from project.firebase_authentication import firebase_admin_required
from .serializer import MemberSerializer, EmailTokenObtainPairSerializer
import traceback


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='post')
class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([AllowAny])
@firebase_admin_required
def get_members(request: HttpRequest) -> Response:
    members = Member.objects.filter(email_confirmed=True).order_by("-join_date")
    serializer = MemberSerializer(members, many=True)
    return Response(serializer.data)

# ==========================================================
# Helpers
# ==========================================================

def _validate_activation_data(data: dict[str, Any]) -> tuple[Response | None, dict[str, Any] | None]:
    member_id = data.get("member_id")
    password = data.get("password")
    deadline = data.get("deadline")
    trainee_code = data.get("trainee_code")

    if not member_id or not password or not deadline:
        return Response(
            {"message": "Missing required fields."},
            status=status.HTTP_400_BAD_REQUEST,
        ), None

    try:
        deadline_date: datetime = datetime.fromisoformat(deadline)
    except ValueError:
        return Response(
            {"message": "Invalid deadline format."},
            status=status.HTTP_400_BAD_REQUEST,
        ), None

    return None, {
        "member_id": member_id,
        "password": password,
        "deadline_date": deadline_date,
        "trainee_code": trainee_code,
    }

def _get_activatable_member(member_id: int) -> tuple[Response | None, Member | None]:
    try:
        member = Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        return Response(
            {"message": "Member not found."},
            status=status.HTTP_404_NOT_FOUND,
        ), None

    if member.user is not None:
        return Response(
            {"message": "This member is already activated."},
            status=status.HTTP_400_BAD_REQUEST,
        ), None

    return None, member

def _create_firebase_trainee(
    member: Member, email: str, password: str, deadline_date: datetime
) -> UserRecord:

    firebase_user: UserRecord = auth.create_user(
        email=email,
        password=password,
    )

    try:
        db = firestore.client()
        db.collection("Trainees").document(firebase_user.uid).set({
            "Uid": firebase_user.uid,
            "MemberId": member.id,
            "Name": member.name,
            "Email": email,
            "Deadline": deadline_date,
            "AccountStatus": True,
            "AccountCreated": True,
            "CreatedAt": firestore.SERVER_TIMESTAMP,
        })
    except Exception:
        try:
            auth.delete_user(firebase_user.uid)
        except Exception:
            traceback.print_exc()
        raise

    return firebase_user

def _rollback_firebase(firebase_user: UserRecord | None) -> None:

    if firebase_user is None:
        return
    try:
        auth.delete_user(firebase_user.uid)
        firestore.client().collection("Trainees").document(firebase_user.uid).delete()
    except Exception:
        traceback.print_exc()

def _activate_member_in_django(
    member: Member,
    email: str,
    password: str,
    firebase_uid: str,
    deadline_date: datetime,
    trainee_code: str | None,
) -> None:
    with transaction.atomic():
        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email},
        )
        user.email = email
        user.set_password(password)
        user.save()

        member.user = user
        member.firebase_uid = firebase_uid
        member.deadline = deadline_date
        member.account_status = True
        member.trainee_code = trainee_code
        member.is_activated = True
        member.save(update_fields=[
            "user", "firebase_uid", "deadline",
            "account_status", "trainee_code", "is_activated",
        ])

        PendingRegistration.objects.filter(email=email).delete()


# ==========================================================
# View
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
@firebase_admin_required
def activate_trainee(request: HttpRequest) -> Response:

    error_response, data = _validate_activation_data(request.data)
    if error_response:
        return error_response

    error_response, member = _get_activatable_member(data["member_id"])
    if error_response:
        return error_response

    email: str = member.email

    firebase_user: UserRecord | None = None
    try:
        firebase_user = _create_firebase_trainee(
            member, email, data["password"], data["deadline_date"]
        )
    except Exception:
        traceback.print_exc()
        return Response(
            {"message": "Failed to create trainee account. Please try again or contact support."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # --- Django User + Member ---
    try:
        _activate_member_in_django(
            member=member,
            email=email,
            password=data["password"],
            firebase_uid=firebase_user.uid,
            deadline_date=data["deadline_date"],
            trainee_code=data["trainee_code"],
        )
    except Exception:
        traceback.print_exc()
        _rollback_firebase(firebase_user)
        return Response(
            {"message": "Failed to finalize trainee activation. Please try again or contact support."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Trainee activated successfully.",
            "firebase_uid": firebase_user.uid,
        },
        status=status.HTTP_201_CREATED,
    )

@api_view(["GET"])
@permission_classes([AllowAny])
@firebase_admin_required
def get_pending_registrations(request: HttpRequest) -> Response:

    members = Member.objects.filter(
        is_activated=False,
        email_confirmed=True,
    ).order_by("-join_date")

    data: list[dict[str, Any]] = [
        {
            "member_id": m.id,
            "name": m.name,
            "email": m.email,
        }
        for m in members
    ]

    return Response(data)
