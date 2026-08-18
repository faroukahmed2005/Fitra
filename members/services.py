import os
import shutil
import traceback
import datetime
from decimal import Decimal

from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.core.signing import TimestampSigner
from django.db import transaction
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
    def __init__(self, pending=None, email_sent=False, email_error=None, duplicate_email=False):
        self.pending = pending          # PendingRegistration instance (replaces old .member)
        self.email_sent = email_sent
        self.email_error = email_error
        self.duplicate_email = duplicate_email

def check_duplicate_email(email):
    if not email:
        return False
    return Member.objects.filter(email=email, is_activated=True).exists()



def _serialize_form_data(data: dict) -> dict:
    safe = {}
    for key, value in data.items():
        if isinstance(value, Decimal):
            safe[key] = str(value)
        elif isinstance(value, datetime.date):
            safe[key] = value.isoformat()
        else:
            safe[key] = value
    return safe


def _deserialize_form_data(raw: dict) -> dict:
    data = dict(raw)
    for field in ('height', 'current_weight'):
        if data.get(field) is not None:
            data[field] = Decimal(data[field])
    if data.get('measurement_date') is not None:
        data['measurement_date'] = datetime.date.fromisoformat(data['measurement_date'])
    return data


def create_pending_registration(data: dict, request) -> RegistrationResult:

    email = data.get('email')
    current_language = request.LANGUAGE_CODE

    if email:
        _delete_pending_registrations_for_email(email)

    serialized = _serialize_form_data(data)

    with transaction.atomic():
        pending = PendingRegistration.objects.create(
            email=email or '',
            preferred_language=current_language,
            form_data=serialized,
        )

        images = request.FILES.getlist('male_photos')
        if images:
            for image in images:
                PendingPicture.objects.create(
                    pending_registration=pending,
                    image=image,
                )

    email_sent = False
    email_error = None

    if email:
        token = signer.sign(pending.id)
        activation_path = reverse(
            'members:activate',
            kwargs={'token': token}
        )

        activation_link = (
            f"{django_settings.PUBLIC_BASE_URL}{activation_path}"
        )

        subject = (
            'تفعيل حسابك في Fitra'
            if current_language == 'ar'
            else 'Activate Your Fitra Account'
        )

        message = render_to_string(
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


def activate_pending_registration(pending: PendingRegistration) -> Member:
    data = _deserialize_form_data(pending.form_data)
    current_language = pending.preferred_language

    with transaction.atomic():
        governorate, _ = Governorate.objects.get_or_create(
            governorate_name=data['place_of_living']
        )

        member = Member.objects.create(
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
            email=pending.email,
            telegram_username=data.get('telegram_user'),
            plan=data['plan_type'],
            recommend_us=data['recommendation_rating'],
            meals_num=data['meals_per_day'],
            daily_spend=data['food_budget'],
            measure_scale=data['measuring_scale'],
            workout_days=data['workout_days'],
            training_type=data['training_location'],
            habits=data['habit'],
            before_nutrition=data['past_nutrition'],
            injuries=data['illness'],
            another_sports=data.get('other_sports'),
            previous_gym=data['gym_before'],
            confidence=data['confidence'],
            comeback=data['return_continuity'],
            preferred_language=current_language,
            is_activated=False,
        )

        Goals.objects.bulk_create([
            Goals(member=member, goal=goal)
            for goal in data['fitness_goal']
        ])

        HearAboutUs.objects.bulk_create([
            HearAboutUs(member=member, source=source)
            for source in data.get('how_hear', [])
        ])

        pending_pictures = list(pending.pending_pictures.all())
        for pp in pending_pictures:
            src_path = pp.image.path                    
            filename = os.path.basename(src_path)
            dest_rel = f'members/{filename}'               
            dest_path = os.path.join(
                django_settings.MEDIA_ROOT, 'members', filename
            )

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            try:
                shutil.move(src_path, dest_path)
            except (OSError, shutil.Error) as exc:
                traceback.print_exc()
                try:
                    shutil.copy2(src_path, dest_path)
                except Exception:
                    traceback.print_exc()
                    dest_rel = pp.image.name  
            Picture.objects.create(member=member, images=dest_rel)
        pending.delete()

    return member

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