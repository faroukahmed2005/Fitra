import os
import shutil
import traceback
import datetime
from decimal import Decimal
from typing import Any

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.db import transaction
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse

from .models import (
    Goals,
    Governorate,
    HearAboutUs,
    Member,
    PendingPicture,
    PendingRegistration,
    Picture,
)

signer = TimestampSigner()


class RegistrationResult:
    def __init__(
        self,
        pending: PendingRegistration | None = None,
        email_sent: bool = False,
        email_error: str | None = None,
        duplicate_email: bool = False,
    ) -> None:
        self.pending = pending
        self.email_sent = email_sent
        self.email_error = email_error
        self.duplicate_email = duplicate_email


def check_duplicate_email(email: str | None) -> bool:
    """Returns True if a confirmed Member already exists with this email."""
    if not email:
        return False
    return Member.objects.filter(email=email, email_confirmed=True).exists()


def _serialize_form_data(data: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            safe[key] = str(value)
        elif isinstance(value, datetime.date):
            safe[key] = value.isoformat()
        else:
            safe[key] = value
    return safe


def _deserialize_form_data(raw: dict[str, Any]) -> dict[str, Any]:
    data = dict(raw)
    for field in ('height', 'current_weight'):
        if data.get(field) is not None:
            data[field] = Decimal(data[field])
    if data.get('measurement_date') is not None:
        data['measurement_date'] = datetime.date.fromisoformat(data['measurement_date'])
    return data


# --------------------------------------------------------------------------- #
#  Public entry-point: create a PendingRegistration for either path
# --------------------------------------------------------------------------- #

def create_pending_registration(
    data: dict[str, Any],
    request: HttpRequest,
    renewal_target_member_id: int | None = None,
) -> RegistrationResult:
    """
    Creates a PendingRegistration and sends the activation email.

    For the New path:
      - email comes from form data
      - renewal_target_member_id is None

    For the Renewal path:
      - email comes from the existing Member record (looked up by
        renewal_target_member_id) — the form has no email input in that path
      - renewal_target_member_id is set so activation knows to UPDATE the
        existing Member rather than create a new one
    """
    current_language: str = request.LANGUAGE_CODE

    if renewal_target_member_id is not None:
        # ---------- Renewal: look up the stored email ---------- #
        try:
            existing_member = Member.objects.get(id=renewal_target_member_id)
        except Member.DoesNotExist:
            # Should not happen — form already validated the ID, but be safe.
            return RegistrationResult(
                email_sent=False,
                email_error=f"Member with id={renewal_target_member_id} not found.",
            )
        email: str = existing_member.email
    else:
        # ---------- New: email typed by the user ---------- #
        email = data.get('email') or ''

    # For New path: clean up any stale pending record for this email.
    # For Renewal path: clean up stale pending records for this email too,
    # so we don't leave orphaned entries.
    if email:
        _delete_pending_registrations_for_email(email)

    serialized = _serialize_form_data(data)

    with transaction.atomic():
        pending = PendingRegistration.objects.create(
            email=email,
            preferred_language=current_language,
            form_data=serialized,
            renewal_target_member_id=renewal_target_member_id,
        )

        images = request.FILES.getlist('male_photos')
        if images:
            for image in images:
                PendingPicture.objects.create(
                    pending_registration=pending,
                    image=image,
                )

    email_sent: bool = False
    email_error: str | None = None

    if email:
        token: str = signer.sign(pending.id)
        activation_path: str = reverse('members:activate', kwargs={'token': token})
        activation_link: str = f"{django_settings.PUBLIC_BASE_URL}{activation_path}"

        subject: str = (
            'تفعيل حسابك في Fitra'
            if current_language == 'ar'
            else 'Activate Your Fitra Account'
        )

        message: str = render_to_string(
            'members/activation_email.html',
            {
                'name': data['full_name'],
                'activation_link': activation_link,
                'language': current_language,
            },
        )

        try:
            send_mail(
                subject,
                '',
                django_settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message,
                fail_silently=False,
            )
            email_sent = True
        except Exception as e:
            email_error = str(e)
            traceback.print_exc()

    return RegistrationResult(
        pending=pending,
        email_sent=email_sent,
        email_error=email_error,
    )


# --------------------------------------------------------------------------- #
#  Activation: called when the user clicks the email link
# --------------------------------------------------------------------------- #

def activate_pending_registration(pending: PendingRegistration) -> Member:
    """
    Activates a PendingRegistration.

    - If renewal_target_member_id is None  → create a brand-new Member (New path).
    - If renewal_target_member_id is set   → update the existing Member (Renewal path).

    In the Renewal path:
      • All form-submitted fields on the existing Member are overwritten.
      • Goals and HearAboutUs rows are replaced (old deleted, new bulk_created)
        because the person may have different goals/answers on renewal.
      • Pictures are replaced the same way (old deleted, new ones moved in).
      • is_activated is reset to False so the member re-enters the coach's
        pending-trainees queue in the mobile app.
      • email_confirmed stays True (email was already confirmed originally
        and hasn't changed — the email came from our own DB, not typed again).
    """
    data = _deserialize_form_data(pending.form_data)
    current_language: str = pending.preferred_language

    with transaction.atomic():
        governorate, _ = Governorate.objects.get_or_create(
            governorate_name=data['place_of_living']
        )

        # Build the dict of field values common to both create and update
        member_fields: dict[str, Any] = dict(
            name=data['full_name'],
            age=data['age'],
            height=data['height'],
            weight=data['current_weight'],
            weight_measure_date=data['measurement_date'],
            gender=data['gender'],
            sizes=data.get('female_measurements', ''),
            education=data['occupation'],
            place=governorate,
            whatsapp_number=data['phone'],
            telegram_username=data.get('telegram_user'),
            plan=data['plan_type'],
            recommend_us=data['recommendation_rating'],
            meals_num=data['meals_per_day'],
            daily_spend=data['food_budget'],
            workout_days=data['workout_days'],
            training_type=data['training_location'],
            habits=data['habit'],
            another_sports=data.get('other_sports'),
            previous_gym=data.get('gym_before', ''),
            lifestyle_commitment=data['lifestyle_commitment'],
            comeback=data['return_continuity'],
            preferred_language=current_language,
            # New fields
            training_age=data.get('training_age'),
            gym_sets_per_week=data.get('gym_sets_per_week'),
            failure_rir=data.get('failure_rir'),
            gym_bench_move=data.get('gym_bench_move'),
            training_time=data.get('training_time'),
            session_duration=data.get('session_duration'),
            daily_steps=data.get('daily_steps'),
            current_split=data.get('current_split'),
            goal_timeframe=data.get('goal_timeframe'),
            wanted_exercise=data.get('wanted_exercise'),
            unwanted_exercise=data.get('unwanted_exercise'),
            chronic_illness=data.get('chronic_illness'),
            injury_issue=data.get('injury_issue'),
            medication=data.get('medication'),
            allergy=data.get('allergy'),
            breakfast=data.get('breakfast'),
            lunch=data.get('lunch'),
            dinner=data.get('dinner'),
            liked_food=data.get('liked_food'),
            disliked_food=data.get('disliked_food'),
            favorite_meal=data.get('favorite_meal'),
            snack_preference=data.get('snack_preference'),
            wanted_diet_food=data.get('wanted_diet_food'),
            daily_drinks=data.get('daily_drinks'),
            trainer_before=data.get('trainer_before'),
            trainer_problem=data.get('trainer_problem'),
            subscribe_reason=data.get('subscribe_reason'),
        )

        if pending.renewal_target_member_id is not None:
            # ---- RENEWAL PATH: update existing Member ---- #
            member: Member = Member.objects.get(id=pending.renewal_target_member_id)

            for field_name, value in member_fields.items():
                setattr(member, field_name, value)
            # Re-enter the pending-trainees queue, keep email confirmed
            member.is_activated = False
            member.email_confirmed = True
            member.save()

            # Replace Goals: delete old, create new
            member.user_goals.all().delete()
            Goals.objects.bulk_create([
                Goals(member=member, goal=goal)
                for goal in data.get('fitness_goal', [])
            ])

            # Replace HearAboutUs: delete old, create new
            member.hear_about_us.all().delete()
            HearAboutUs.objects.bulk_create([
                HearAboutUs(member=member, source=source)
                for source in data.get('how_hear', [])
            ])

            # Replace Pictures: delete old files and DB rows, then move new ones in
            for old_pic in member.user_images.all():
                try:
                    if old_pic.images and os.path.isfile(old_pic.images.path):
                        os.remove(old_pic.images.path)
                except Exception:
                    traceback.print_exc()
            member.user_images.all().delete()

        else:
            # ---- NEW PATH: create brand-new Member ---- #
            member = Member.objects.create(
                email=pending.email,
                is_activated=False,
                email_confirmed=True,
                **member_fields,
            )

            Goals.objects.bulk_create([
                Goals(member=member, goal=goal)
                for goal in data.get('fitness_goal', [])
            ])

            HearAboutUs.objects.bulk_create([
                HearAboutUs(member=member, source=source)
                for source in data.get('how_hear', [])
            ])

        # ---- Move pending pictures to permanent member storage ---- #
        pending_pictures = list(pending.pending_pictures.all())
        for pp in pending_pictures:
            src_path: str = pp.image.path
            filename: str = os.path.basename(src_path)
            dest_rel: str = f'members/{filename}'
            dest_path: str = os.path.join(
                django_settings.MEDIA_ROOT, 'members', filename
            )
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            try:
                shutil.move(src_path, dest_path)
            except (OSError, shutil.Error):
                traceback.print_exc()
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception:
                    traceback.print_exc()
                    dest_rel = pp.image.name
            Picture.objects.create(member=member, images=dest_rel)

        pending.delete()

    return member


# --------------------------------------------------------------------------- #
#  Helpers
# --------------------------------------------------------------------------- #

def _delete_pending_registrations_for_email(email: str) -> None:
    qs = PendingRegistration.objects.filter(email=email)
    for pr in qs:
        _delete_pending_picture_files(pr)
    qs.delete()


def _delete_pending_picture_files(pending: PendingRegistration) -> None:
    for pp in pending.pending_pictures.all():
        try:
            if pp.image and os.path.isfile(pp.image.path):
                os.remove(pp.image.path)
        except Exception:
            traceback.print_exc()
