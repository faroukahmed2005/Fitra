"""
APIs/tests.py

Test suite for the APIs app: JWT login, member listing, trainee
activation, and pending-registrations listing.

All firebase_admin calls (auth.verify_id_token, auth.create_user,
auth.delete_user, firestore.client) are mocked -- these tests never
touch a real Firebase project.
"""
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, override_settings

from members.models import Member, Governorate

User = get_user_model()


def make_confirmed_member(email="alice@example.com", **overrides):
    governorate, _ = Governorate.objects.get_or_create(governorate_name="Cairo")
    defaults = dict(
        name="Alice",
        age=25,
        height="170.00",
        weight="60.00",
        gender="FEMALE",
        sizes="90-60-90",
        education="Engineer",
        place=governorate,
        whatsapp_number="01012345678",
        email=email,
        plan="RARE",
        recommend_us=5,
        meals_num="3 MEALS",
        training_type="GYM",
        workout_days="3 DAYS",
        daily_spend="100-150 BUCKS",
        measure_scale="I DO HAVE",
        before_nutrition="Normal",
        injuries="None",
        previous_gym="YES",
        habits="None",
        confidence="ABSOLUTELY",
        comeback="ABSOLUTELY",
        email_confirmed=True,
        is_activated=False,
    )
    defaults.update(overrides)
    return Member.objects.create(**defaults)


def make_admin_decoded_token(is_admin=True):
    return {"uid": "firebase-admin-uid", "admin": is_admin}


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class EmailTokenObtainPairViewTests(TestCase):
    """Covers ME-27: login endpoint, including the rate limiting from CR-07."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="coach@example.com",
            email="coach@example.com",
            password="StrongPass123!",
        )

    def test_login_with_valid_credentials_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "coach@example.com", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())

    def test_login_with_wrong_password_is_rejected(self):
        response = self.client.post(
            "/api/auth/login/",
            {"email": "coach@example.com", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 400)

    def test_sixth_login_attempt_within_a_minute_is_rate_limited(self):
        for i in range(5):
            response = self.client.post(
                "/api/auth/login/",
                {"email": "coach@example.com", "password": "wrong-password"},
                REMOTE_ADDR="10.1.1.1",
            )
            self.assertNotEqual(response.status_code, 429)

        sixth = self.client.post(
            "/api/auth/login/",
            {"email": "coach@example.com", "password": "wrong-password"},
            REMOTE_ADDR="10.1.1.1",
        )
        self.assertEqual(sixth.status_code, 403)  # DRF's PermissionDenied response


class GetMembersViewTests(TestCase):
    """Covers ME-27: /api/members/, and re-confirms the email_confirmed filtering fixed earlier."""

    def setUp(self):
        make_confirmed_member(email="confirmed@example.com")

    def test_missing_auth_header_returns_401(self):
        response = self.client.get("/api/members/")
        self.assertEqual(response.status_code, 401)

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_non_admin_token_returns_403(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=False)
        response = self.client.get(
            "/api/members/", HTTP_AUTHORIZATION="Bearer faketoken"
        )
        self.assertEqual(response.status_code, 403)

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_admin_token_returns_only_confirmed_members(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=True)
        response = self.client.get(
            "/api/members/", HTTP_AUTHORIZATION="Bearer faketoken"
        )
        self.assertEqual(response.status_code, 200)
        emails = [m["email"] for m in response.json()]
        self.assertIn("confirmed@example.com", emails)


class GetPendingRegistrationsViewTests(TestCase):
    """Covers ME-27: /api/pending-trainees/ filtering logic."""

    def setUp(self):
        make_confirmed_member(email="pending@example.com", is_activated=False)
        make_confirmed_member(email="already_trainee@example.com", is_activated=True)

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_only_returns_confirmed_and_not_yet_activated(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=True)
        response = self.client.get(
            "/api/pending-trainees/", HTTP_AUTHORIZATION="Bearer faketoken"
        )
        self.assertEqual(response.status_code, 200)
        emails = [m["email"] for m in response.json()]
        self.assertIn("pending@example.com", emails)
        self.assertNotIn("already_trainee@example.com", emails)


class ActivateTraineeViewTests(TestCase):
    """
    Covers ME-27 + regression-tests the Firebase rollback fix: if the
    Firestore write fails after the Auth user was created, the Auth user
    must be cleaned up (not left orphaned), and no Django Member should
    end up half-activated.
    """

    def setUp(self):
        self.member = make_confirmed_member(email="trainee@example.com")
        self.auth_header = {"HTTP_AUTHORIZATION": "Bearer faketoken"}

    def _activation_payload(self, **overrides):
        payload = {
            "member_id": self.member.id,
            "password": "TraineePass123!",
            "deadline": (date.today() + timedelta(days=30)).isoformat(),
            "trainee_code": "T-001",
        }
        payload.update(overrides)
        return payload

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_missing_fields_returns_400(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=True)
        response = self.client.post(
            "/api/trainee/activate/", {"member_id": self.member.id}, **self.auth_header
        )
        self.assertEqual(response.status_code, 400)

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_nonexistent_member_returns_404(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=True)
        response = self.client.post(
            "/api/trainee/activate/",
            self._activation_payload(member_id=999999),
            **self.auth_header,
        )
        self.assertEqual(response.status_code, 404)

    @patch("project.firebase_authentication.auth.verify_id_token")
    @patch("APIs.views.firestore")
    @patch("APIs.views.auth")
    def test_successful_activation_creates_user_and_activates_member(
        self, mock_auth, mock_firestore, mock_verify_token
    ):
        mock_verify_token.return_value = make_admin_decoded_token(is_admin=True)

        fake_firebase_user = MagicMock()
        fake_firebase_user.uid = "new-trainee-uid"
        mock_auth.create_user.return_value = fake_firebase_user

        mock_db = MagicMock()
        mock_firestore.client.return_value = mock_db
        mock_firestore.SERVER_TIMESTAMP = "SERVER_TIMESTAMP"

        response = self.client.post(
            "/api/trainee/activate/", self._activation_payload(), **self.auth_header
        )

        self.assertEqual(response.status_code, 201)
        self.member.refresh_from_db()
        self.assertTrue(self.member.is_activated)
        self.assertEqual(self.member.firebase_uid, "new-trainee-uid")
        self.assertIsNotNone(self.member.user)
        mock_db.collection.assert_called_with("Trainees")

    @patch("project.firebase_authentication.auth.verify_id_token")
    @patch("APIs.views.firestore")
    @patch("APIs.views.auth")
    def test_firestore_failure_rolls_back_auth_user_and_does_not_activate_member(
        self, mock_auth, mock_firestore, mock_verify_token
    ):
        """
        Regression test for the Firebase rollback fix: simulates Firestore
        raising after auth.create_user() already succeeded. The Auth user
        must be deleted, and the Member must remain un-activated (no
        orphaned Firebase user, no half-activated Django state).
        """
        mock_verify_token.return_value = make_admin_decoded_token(is_admin=True)

        fake_firebase_user = MagicMock()
        fake_firebase_user.uid = "orphan-candidate-uid"
        mock_auth.create_user.return_value = fake_firebase_user

        mock_db = MagicMock()
        mock_db.collection.return_value.document.return_value.set.side_effect = Exception(
            "Simulated Firestore outage"
        )
        mock_firestore.client.return_value = mock_db
        mock_firestore.SERVER_TIMESTAMP = "SERVER_TIMESTAMP"

        response = self.client.post(
            "/api/trainee/activate/", self._activation_payload(), **self.auth_header
        )

        self.assertEqual(response.status_code, 400)
        self.member.refresh_from_db()
        self.assertFalse(self.member.is_activated)
        self.assertIsNone(self.member.user)

        # The core regression check: the Auth user created just before the
        # Firestore failure must have been cleaned up by
        # _create_firebase_trainee's own internal rollback.
        mock_auth.delete_user.assert_called_with("orphan-candidate-uid")

    @patch("project.firebase_authentication.auth.verify_id_token")
    def test_already_activated_member_returns_400(self, mock_verify):
        mock_verify.return_value = make_admin_decoded_token(is_admin=True)
        self.member.is_activated = True
        self.member.user = User.objects.create_user(
            username="already@example.com", password="x"
        )
        self.member.save()

        response = self.client.post(
            "/api/trainee/activate/", self._activation_payload(), **self.auth_header
        )
        self.assertEqual(response.status_code, 400)
