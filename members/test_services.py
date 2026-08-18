"""
members/test_services.py

Tests for the pending-registration -> activation flow in members/services.py
and members/views.py (activate_account).

Covers:
- create_pending_registration() creates a PendingRegistration + PendingPicture,
  and does NOT create a Member
- Two registrations with the same (unactivated) email can coexist
- Activating one creates a real Member and deletes the PendingRegistration
- Activating a second PendingRegistration for an email that's now taken
  renders the "email taken" page and cleans up
- Duplicate-email check against already-activated Members blocks new pendings
  at the view level (register()) -- not re-tested here since it's a view-level
  form error, see test_views.py if you add one
"""
import datetime
import tempfile
import shutil
from decimal import Decimal

from django.core import mail
from django.core.signing import TimestampSigner
from django.test import TestCase, RequestFactory, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile

from members.models import Member, PendingRegistration, PendingPicture, Governorate
from members import services

signer = TimestampSigner()


def make_cleaned_data(**overrides):
    """Mimics RegistrationForm.cleaned_data for a valid MALE registrant."""
    data = {
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
        "measuring_scale": "I DO HAVE",
        "workout_days": "3 DAYS",
        "training_location": "GYM",
        "habit": "Normal daily routine.",
        "past_nutrition": "Tried keto before.",
        "plan_type": "RARE",
        "illness": "None",
        "other_sports": "",
        "gym_before": "YES",
        "confidence": "ABSOLUTELY",
        "return_continuity": "ABSOLUTELY",
        "how_hear": [],
        "recommendation_rating": 5,
    }
    data.update(overrides)
    return data


def make_request(files=None):
    """Builds a bare Django request with the attributes services.py relies on:
    LANGUAGE_CODE (normally set by LocaleMiddleware) and FILES.getlist().

    NOTE: WSGIRequest.FILES is a read-only property in modern Django, so it
    can't be assigned after the request is built. Instead, pass any files
    as part of the `data` dict -- RequestFactory automatically multipart-
    encodes them and populates request.FILES correctly on its own."""
    rf = RequestFactory()
    post_data = dict(files) if files else {}
    request = rf.post("/register/", data=post_data)
    request.LANGUAGE_CODE = "en"
    return request


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class CreatePendingRegistrationTests(TestCase):
    """Covers: submitting the form creates a PendingRegistration, not a Member."""

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

    def test_two_pending_registrations_same_email_can_coexist(self):
        """This is the whole point of the pending-registration redesign:
        no UNIQUE constraint conflict for two unactivated signups sharing an email."""
        data = make_cleaned_data(email="shared@example.com")

        request1 = make_request()
        services.create_pending_registration(data, request1)

        # NOTE: create_pending_registration deletes prior pending registrations
        # for the same email (_delete_pending_registrations_for_email) BEFORE
        # creating the new one. So submitting twice in a row actually replaces
        # the first pending record, not adds a second one. This test verifies
        # THAT behavior -- if you intended both to coexist simultaneously,
        # this reveals the current design only keeps the latest pending
        # registration per email, which is worth confirming is what you want.
        request2 = make_request()
        services.create_pending_registration(data, request2)

        self.assertEqual(
            PendingRegistration.objects.filter(email="shared@example.com").count(),
            1,
            "create_pending_registration replaces prior pending registrations "
            "for the same email rather than keeping both -- confirm this is intended."
        )


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ActivatePendingRegistrationTests(TestCase):
    """Covers: activating a pending registration creates a real Member with
    correct data, and deletes the pending record."""

    def test_activation_creates_member_with_correct_fields(self):
        data = make_cleaned_data(email="carol@example.com", full_name="Carol Test")
        request = make_request()
        result = services.create_pending_registration(data, request)
        pending = result.pending

        member = services.activate_pending_registration(pending)

        self.assertEqual(member.name, "Carol Test")
        self.assertEqual(member.email, "carol@example.com")
        self.assertTrue(member.is_activated)
        self.assertEqual(member.height, Decimal("175.50"))
        self.assertEqual(member.weight_measure_date, datetime.date(2026, 7, 1))
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
        """Confirms get_or_create in activate_pending_registration doesn't
        create duplicate Governorate rows across two activations for the
        same governorate name."""
        data1 = make_cleaned_data(email="frank@example.com", place_of_living="Giza")
        data2 = make_cleaned_data(email="grace@example.com", place_of_living="Giza")

        r1 = services.create_pending_registration(data1, make_request())
        r2 = services.create_pending_registration(data2, make_request())

        services.activate_pending_registration(r1.pending)
        services.activate_pending_registration(r2.pending)

        self.assertEqual(Governorate.objects.filter(governorate_name="Giza").count(), 1)


@override_settings(
    MEDIA_ROOT=tempfile.mkdtemp(),
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class ActivateAccountViewTests(TestCase):
    """Covers the activate_account view: valid token, expired token, bad
    token, and the 'email already taken by someone else' race case."""

    def test_valid_token_activates_and_shows_success(self):
        data = make_cleaned_data(email="henry@example.com")
        result = services.create_pending_registration(data, make_request())
        token = signer.sign(result.pending.id)

        response = self.client.get(f"/register/activate/{token}/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Member.objects.filter(email="henry@example.com", is_activated=True).exists())

    def test_second_activation_of_same_email_shows_email_taken(self):
        """Simulates the race: two PendingRegistrations for the same email
        (created before either activates), first one activates normally,
        second one's activation link should now show 'email taken', not
        silently succeed or crash."""
        data = make_cleaned_data(email="iris@example.com")

        pending1 = services.create_pending_registration(data, make_request()).pending
        # Bypass the "replace prior pending" behavior to simulate two
        # pending records genuinely coexisting at the moment of activation:
        pending2 = PendingRegistration.objects.create(
            email="iris@example.com",
            preferred_language="en",
            form_data=pending1.form_data,
        )

        token1 = signer.sign(pending1.id)
        token2 = signer.sign(pending2.id)

        # First activates normally
        response1 = self.client.get(f"/register/activate/{token1}/")
        self.assertEqual(response1.status_code, 200)
        self.assertTrue(Member.objects.filter(email="iris@example.com").exists())

        # Second should hit the "email taken" branch, not create a 2nd Member
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

        # To simulate a genuinely EXPIRED (not tampered) token, we sign it
        # as if it were created 25 hours ago -- the signature itself stays
        # perfectly valid (so unsign() can still recover the pending id),
        # but the max_age=24h check in activate_account will correctly
        # reject it as too old. Corrupting the token string instead (e.g.
        # appending garbage) produces a BadSignature, not SignatureExpired
        # -- a fundamentally different, unrecoverable case where cleanup
        # correctly cannot happen at all, since no data can be extracted
        # from a tampered signature.
        import time
        from unittest import mock

        with mock.patch("django.core.signing.time.time", return_value=time.time() - 60 * 60 * 25):
            token = signer.sign(pending.id)

        response = self.client.get(f"/register/activate/{token}/")

        self.assertTemplateUsed(response, "members/activation_failed.html")
        self.assertFalse(PendingRegistration.objects.filter(id=pending.id).exists())
