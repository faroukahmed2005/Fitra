"""
members/test_ratelimit.py

Tests for the @ratelimit decorator on the register view.
Updated for registration overhaul: old field names replaced with new ones.
"""
from django.core.cache import cache
from django.test import TestCase, override_settings


VALID_POST_DATA = {
    "registration_type": "New",
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
    # Email left blank on purpose: avoids creating a real PendingRegistration
    # / sending real email on every repeated POST (so the form will fail
    # validation but still hit the view, which is all we need for rate-limit testing)
    "email": "",
    "fitness_goal": ["FAT LOSS"],
    "meals_per_day": "3 MEALS",
    "food_budget": "100-150 BUCKS",
    "workout_days": "3 DAYS",
    "training_location": "GYM",
    "gym_bench_move": "CAN MOVE",
    "training_time": "MORNING",
    "session_duration": "1 HOUR",
    "daily_steps": "5000",
    "current_split": "PPL",
    "goal_timeframe": "3 months",
    "habit": "Normal daily routine.",
    "plan_type": "DUOS",
    "gym_before": "YES",
    "gym_sets_per_week": "6-8",
    "training_age": "1 YEAR",
    "failure_rir": "YES I KNOW BOTH",
    "trainer_before": "NO",
    "chronic_illness": "None",
    "medication": "None",
    "allergy": "None",
    "breakfast": "Eggs",
    "lunch": "Rice",
    "dinner": "Salad",
    "liked_food": "Chicken",
    "disliked_food": "Fish",
    "favorite_meal": "Shawarma",
    "wanted_diet_food": "High protein",
    "daily_drinks": "Water",
    "subscribe_reason": "Get fit",
    "lifestyle_commitment": "ABSOLUTELY",
    "return_continuity": "ABSOLUTELY",
    "recommendation_rating": 5,
    "terms_acceptance": True,
}


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
class RegistrationRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_sixth_request_within_a_minute_is_blocked(self):
        """5 requests pass; the 6th should be blocked with 429."""
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

        response = self.client.post("/register/", data=VALID_POST_DATA, REMOTE_ADDR="10.0.0.3")
        self.assertNotEqual(response.status_code, 429)
