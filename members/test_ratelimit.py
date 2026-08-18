"""
members/test_ratelimit.py

Tests for the @ratelimit decorator on the register view (item #6).
Uses Django's test client and the default LocMemCache (django-ratelimit
needs a working cache backend to count hits).
"""
from django.core.cache import cache
from django.test import TestCase, override_settings


VALID_POST_DATA = {
    "full_name": "Rate Limit Test",
    "age": 25,
    "height": "175.50",
    "current_weight": "80.00",
    "measurement_date": "2026-07-01",
    "gender": "FEMALE",
    "female_measurements": "90-60-90",
    "occupation": "Engineer",
    "place_of_living": "Cairo",
    "phone": "01012345678",
    "email": "",  # left blank on purpose: avoids creating a real
                  # PendingRegistration/sending real email on every one
                  # of these repeated POSTs; email is optional per the form
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
    "gym_before": "YES",
    "confidence": "ABSOLUTELY",
    "return_continuity": "ABSOLUTELY",
    "recommendation_rating": 5,
}


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class RegistrationRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_sixth_request_within_a_minute_is_blocked(self):
        """The decorator is @ratelimit(key='ip', rate='5/m', method='POST', block=True).
        5 requests should go through (accepted by the view -- may still be a
        200 with form errors, that's fine, we're only checking it's not
        rate-limited); the 6th should be blocked with a 429."""
        for i in range(5):
            response = self.client.post(
                "/register/",
                data=VALID_POST_DATA,
                REMOTE_ADDR="10.0.0.1",
            )
            self.assertNotEqual(
                response.status_code, 429,
                f"Request {i + 1} was unexpectedly rate-limited"
            )

        sixth_response = self.client.post(
            "/register/",
            data=VALID_POST_DATA,
            REMOTE_ADDR="10.0.0.1",
        )
        self.assertEqual(sixth_response.status_code, 429)

    def test_different_ips_are_limited_independently(self):
        for i in range(5):
            self.client.post("/register/", data=VALID_POST_DATA, REMOTE_ADDR="10.0.0.2")

        # A different IP should not be affected by the first IP's usage
        response = self.client.post("/register/", data=VALID_POST_DATA, REMOTE_ADDR="10.0.0.3")
        self.assertNotEqual(response.status_code, 429)
