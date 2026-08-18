from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from .serializer import MemberSerializer, EmailTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework import status

from firebase_admin import auth, firestore
from datetime import datetime
from django.db import transaction
from firebase_admin import exceptions as firebase_exceptions
from members.models import Member, PendingRegistration
from project.firebase_authentication import firebase_admin_required
from rest_framework.permissions import AllowAny
import traceback


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([AllowAny])
@firebase_admin_required
def get_members(request):
    members = Member.objects.all().order_by("-join_date")
    serializer = MemberSerializer(members, many=True)
    return Response(serializer.data)

# ==========================================================
# Helpers
# ==========================================================

def _validate_activation_data(data):
    """يتحقق من وجود الحقول المطلوبة ويرجع (errors_response, cleaned_data)"""
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
        deadline_date = datetime.fromisoformat(deadline)
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

def _get_activatable_member(member_id):
    """يرجع (error_response, member)"""
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

def _create_firebase_trainee(member, email, password, deadline_date):
    firebase_user = auth.create_user(
        email=email,
        password=password,
    )

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

    return firebase_user

def _rollback_firebase(firebase_user):
    """يحذف يوزر Firebase ومستنده لو حصل فشل بعد إنشائه"""
    if firebase_user is None:
        return
    try:
        auth.delete_user(firebase_user.uid)
        firestore.client().collection("Trainees").document(firebase_user.uid).delete()
    except Exception:
        pass

def _activate_member_in_django(member, email, password, firebase_uid, deadline_date, trainee_code):
    """ينشئ/يحدّث Django User ويربطه بالـ Member، جوه transaction"""
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
def activate_trainee(request):

    error_response, data = _validate_activation_data(request.data)
    if error_response:
        return error_response

    error_response, member = _get_activatable_member(data["member_id"])
    if error_response:
        return error_response

    email = member.email

    # --- Firebase + Firestore ---
    firebase_user = None
    try:
        firebase_user = _create_firebase_trainee(
            member, email, data["password"], data["deadline_date"]
        )
    except Exception as e:
        traceback.print_exc()
        _rollback_firebase(firebase_user)
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
    except Exception as e:
        _rollback_firebase(firebase_user)
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
def get_pending_registrations(request):

    members = Member.objects.filter(is_activated=False).order_by("-join_date")

    data = [
        {
            "member_id": m.id,
            "name": m.name,
            "email": m.email,
        }
        for m in members
    ]

    return Response(data)