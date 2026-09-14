"""
members/test_services.py

Tests for the pending-registration -> activation flow.
Updated for registration overhaul:
- illness -> chronic_illness + injury_issue
- measuring_scale removed
- past_nutrition removed
- confidence -> lifestyle_commitment
- plan_type RARE -> DUOS
- return_continuity NOT SURE -> NO
- New fields added to make_cleaned_data
- Renewal path: renewal_target_member_id, activate updates existing Member
"""
import datetime
import tempfile
import shutil
from decimal import Decimal
from unittest import mock

from django.core import mail
from django.core.signing import TimestampSigner
from django.test import TestCase, RequestFactory, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from members.models import Member, PendingRegistration, PendingPicture, Governorate
from members import services

signer = TimestampSigner()


def make_cleaned_data(**overrides):
    """Mimics RegistrationForm.cleaned_data for a valid MALE New registrant."""
    data = {
        "registration_type": "New",
        "full_name": "Test User",
        "age": 25,
        "height": Decimal("175.50"),
        "current_weight": Decimal("80.00"),
        "measurement_date": datetime.date(2026, 7, 1),
        "gender": "MALE",
        "female_measurements": "",
        "occupation": "Engineer",
        "place_of_living": "Cairo",
        "phone": "01012345678",
        "email": "test@example.com",
        "telegram_user": "",
        "fitness_goal": ["FAT LOSS"],
        "meals_per_day": "3 MEALS",
        "food_budget": "100-150 BUCKS",
        "workout_days": "3 DAYS",
        "training_location": "GYM",
        "training_time": "MORNING",
        "session_duration": "1 HOUR",
        "daily_steps": "5000",
        "current_split": "PPL",
        "goal_timeframe": "3 months",
        "habit": "Normal daily routine.",
        "other_sports": "",
        "plan_type": "DUOS",
        # Training background
        "gym_before": "YES",
        "gym_sets_per_week": "6-8",
        "training_age": "1 YEAR",
        "failure_rir": "YES I KNOW BOTH",
        "gym_bench_move": "CAN MOVE",
        "trainer_before": "NO",
        "trainer_problem": "",
        # Health
        "chronic_illness": "None",
        "injury_issue": "",
        "medication": "None",
        "allergy": "None",
        # Nutrition
        "breakfast": "Eggs",
        "lunch": "Rice",
        "dinner": "Salad",
        "liked_food": "Chicken",
        "disliked_food": "Fish",
        "favorite_meal": "Shawarma",
        "snack_preference": "",
        "wanted_diet_food": "High protein",
        "daily_drinks": "Water",
        # Motivation
        "subscribe_reason": "Get fit",
        "lifestyle_commitment": "ABSOLUTELY",
        "return_continuity": "ABSOLUTELY",
        "how_hear": [],
        "recommendation_rating": 5,
        "terms_acceptance": True,
    }
    data.update(overrides)
    return data


def make_request(files=None):
    rf = RequestFactory()
    post_data = dict(files) if files else {}
    request = rf.post("/register/", data=post_data)
    request.LANGUAGE_CODE = "en"
    return request


def _make_existing_member():
    """Create a confirmed Member for use in Renewal tests."""
    gov, _ = Governorate.objects.get_or_create(governorate_name="Cairo")
    return Member.objects.create(
        name="Existing User",
        age=30,
        height=Decimal("175.00"),
        weight=Decimal("80.00"),
        gender="MALE",
        education="Engineer",
        place=gov,
        whatsapp_number="01099999999",
        email="existing@example.com",
        email_confirmed=True,
        plan="DUOS",
        recommend_us=4,
        meals_num="3 MEALS",
        training_type="GYM",
        workout_days="3 DAYS",
        daily_spend="100-150 BUCKS",
        previous_gym="YES",
        habits="Normal",
        lifestyle_commitment="ABSOLUTELY",
        comeback="ABSOLUTELY",
        is_activated=False,
    )


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class CreatePendingRegistrationTests(TestCase):
    """create_pending_registration() creates PendingRegistration, not Member."""

    def test_creates_pending_registration_not_member(self):
        data = make_cleaned_data(email="alice@example.com")
        request = make_request()
        result = services.create_pending_registration(data, request)
        self.assertIsNotNone(result.pending)
        self.assertEqual(PendingRegistration.objects.count(), 1)
        self.assertEqual(Member.objects.count(), 0)
        self.assertTrue(result.email_sent)
        self.assertEqual(len(mail.outbox), 1)

    def test_creates_pending_pictures_from_uploaded_files(self):
        photo = SimpleUploadedFile("p1.jpg", b"\xff\xd8\xff" + b"0" * 100, content_type="image/jpeg")
        data = make_cleaned_data(email="bob@example.com")
        request = make_request(files={"male_photos": [photo]})
        result = services.create_pending_registration(data, request)
        self.assertEqual(PendingPicture.objects.filter(pending_registration=result.pending).count(), 1)

    def test_two_pending_registrations_same_email_replaces_first(self):
        """Submitting twice with same email replaces the first pending record."""
        data = make_cleaned_data(email="shared@example.com")
        services.create_pending_registration(data, make_request())
        services.create_pending_registration(data, make_request())
        self.assertEqual(
            PendingRegistration.objects.filter(email="shared@example.com").count(),
            1,
        )

    def test_email_send_failure_still_creates_pending_registration(self):
        data = make_cleaned_data(email="unlucky@example.com")
        request = make_request()
        with mock.patch("members.services.send_mail", side_effect=Exception("Simulated SMTP failure")):
            result = services.create_pending_registration(data, request)
        self.assertIsNotNone(result.pending)
        self.assertEqual(PendingRegistration.objects.filter(email="unlucky@example.com").count(), 1)
        self.assertFalse(result.email_sent)
        self.assertIn("Simulated SMTP failure", result.email_error)


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ActivatePendingRegistrationTests(TestCase):
    """Activating a pending registration creates a real Member."""

    def test_activation_creates_member_with_correct_fields(self):
        data = make_cleaned_data(email="carol@example.com", full_name="Carol Test")
        request = make_request()
        result = services.create_pending_registration(data, request)
        pending = result.pending

        member = services.activate_pending_registration(pending)

        self.assertEqual(member.name, "Carol Test")
        self.assertEqual(member.email, "carol@example.com")
        self.assertTrue(member.email_confirmed)
        self.assertEqual(member.height, Decimal("175.50"))
        self.assertEqual(member.weight_measure_date, datetime.date(2026, 7, 1))
        # Verify new fields
        self.assertEqual(member.lifestyle_commitment, "ABSOLUTELY")
        self.assertEqual(member.plan, "DUOS")
        self.assertFalse(member.is_activated)
        self.assertEqual(PendingRegistration.objects.filter(id=pending.id).count(), 0)

    def test_activation_creates_goals_and_hear_about_us(self):
        data = make_cleaned_data(
            email="dave@example.com",
            fitness_goal=["FAT LOSS", "INCREASE MUSCLE MASS"],
            how_hear=["FACEBOOK", "A FRIEND"],
        )
        request = make_request()
        result = services.create_pending_registration(data, request)
        member = services.activate_pending_registration(result.pending)
        self.assertEqual(member.user_goals.count(), 2)
        self.assertEqual(member.hear_about_us.count(), 2)

    def test_activation_moves_pending_pictures_to_member(self):
        photo = SimpleUploadedFile("p1.jpg", b"\xff\xd8\xff" + b"0" * 100, content_type="image/jpeg")
        data = make_cleaned_data(email="erin@example.com")
        request = make_request(files={"male_photos": [photo]})
        result = services.create_pending_registration(data, request)
        member = services.activate_pending_registration(result.pending)
        self.assertEqual(member.user_images.count(), 1)

    def test_activation_reuses_existing_governorate(self):
        data1 = make_cleaned_data(email="frank@example.com", place_of_living="Giza")
        data2 = make_cleaned_data(email="grace@example.com", place_of_living="Giza")
        r1 = services.create_pending_registration(data1, make_request())
        r2 = services.create_pending_registration(data2, make_request())
        services.activate_pending_registration(r1.pending)
        services.activate_pending_registration(r2.pending)
        self.assertEqual(Governorate.objects.filter(governorate_name="Giza").count(), 1)

    def test_activation_new_fields_stored(self):
        """Verify the new fields introduced in the overhaul are persisted."""
        data = make_cleaned_data(
            email="newfields@example.com",
            chronic_illness="Diabetes",
            medication="Metformin",
            allergy="Nuts",
            breakfast="Oats",
            lunch="Rice and chicken",
            dinner="Salad",
            liked_food="Chicken",
            disliked_food="Fish",
            favorite_meal="Shawarma",
            wanted_diet_food="High protein meals",
            daily_drinks="2L water",
            subscribe_reason="Lose weight",
            training_age="1 YEAR",
            failure_rir="YES I KNOW BOTH",
        )
        result = services.create_pending_registration(data, make_request())
        member = services.activate_pending_registration(result.pending)
        self.assertEqual(member.chronic_illness, "Diabetes")
        self.assertEqual(member.medication, "Metformin")
        self.assertEqual(member.allergy, "Nuts")
        self.assertEqual(member.breakfast, "Oats")
        self.assertEqual(member.training_age, "1 YEAR")
        self.assertEqual(member.failure_rir, "YES I KNOW BOTH")
        self.assertEqual(member.subscribe_reason, "Lose weight")


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class RenewalActivationTests(TestCase):
    """Renewal path: activate updates existing Member instead of creating new one."""

    def test_renewal_updates_existing_member(self):
        existing = _make_existing_member()
        data = make_cleaned_data(
            registration_type="Renewal",
            full_name="Updated Name",
            email=existing.email,  # won't be used for lookup but included in data
        )
        # Remove email from data as form does for Renewal path
        data.pop("email", None)

        request = make_request()
        result = services.create_pending_registration(
            data, request, renewal_target_member_id=existing.id
        )
        self.assertEqual(result.pending.renewal_target_member_id, existing.id)
        self.assertEqual(result.pending.email, existing.email)

        updated_member = services.activate_pending_registration(result.pending)

        # Should be the SAME member object, not a new one
        self.assertEqual(updated_member.id, existing.id)
        self.assertEqual(updated_member.name, "Updated Name")
        # is_activated reset to False, email_confirmed stays True
        self.assertFalse(updated_member.is_activated)
        self.assertTrue(updated_member.email_confirmed)
        # PendingRegistration cleaned up
        self.assertEqual(PendingRegistration.objects.filter(id=result.pending.id).count(), 0)
        # No duplicate Member created
        self.assertEqual(Member.objects.filter(email=existing.email).count(), 1)

    def test_renewal_replaces_goals(self):
        from members.models import Goals
        existing = _make_existing_member()
        Goals.objects.create(member=existing, goal="FAT LOSS")
        Goals.objects.create(member=existing, goal="HAVING FUN")

        data = make_cleaned_data(
            registration_type="Renewal",
            fitness_goal=["INCREASE MUSCLE MASS"],
        )
        result = services.create_pending_registration(
            data, make_request(), renewal_target_member_id=existing.id
        )
        updated = services.activate_pending_registration(result.pending)

        goals = list(updated.user_goals.values_list("goal", flat=True))
        self.assertEqual(goals, ["INCREASE MUSCLE MASS"])


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ActivateAccountViewTests(TestCase):
    """activate_account view: valid token, expired, bad token, email-taken race."""

    def test_valid_token_activates_and_shows_success(self):
        data = make_cleaned_data(email="henry@example.com")
        result = services.create_pending_registration(data, make_request())
        token = signer.sign(result.pending.id)
        response = self.client.get(f"/register/activate/{token}/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Member.objects.filter(email="henry@example.com", email_confirmed=True).exists())

    def test_second_activation_of_same_email_shows_email_taken(self):
        data = make_cleaned_data(email="iris@example.com")
        pending1 = services.create_pending_registration(data, make_request()).pending
        pending2 = PendingRegistration.objects.create(
            email="iris@example.com",
            preferred_language="en",
            form_data=pending1.form_data,
        )
        token1 = signer.sign(pending1.id)
        token2 = signer.sign(pending2.id)

        response1 = self.client.get(f"/register/activate/{token1}/")
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(Member.objects.filter(email="iris@example.com").exists())

        response2 = self.client.get(f"/register/activate/{token2}/")
        self.assertTemplateUsed(response2, "members/email_taken.html")
        self.assertEqual(Member.objects.filter(email="iris@example.com").count(), 1)
        self.assertFalse(PendingRegistration.objects.filter(id=pending2.id).exists())

    def test_invalid_token_shows_activation_failed(self):
        response = self.client.get("/register/activate/not-a-real-token/")
        self.assertTemplateUsed(response, "members/activation_failed.html")

    def test_expired_token_shows_activation_failed_and_cleans_up(self):
        data = make_cleaned_data(email="jack@example.com")
        pending = services.create_pending_registration(data, make_request()).pending
        import time
        with mock.patch("django.core.signing.time.time", return_value=time.time() - 60 * 60 * 25):
            token = signer.sign(pending.id)
        response = self.client.get(f"/register/activate/{token}/")
        self.assertTemplateUsed(response, "members/activation_failed.html")
        self.assertFalse(PendingRegistration.objects.filter(id=pending.id).exists())
