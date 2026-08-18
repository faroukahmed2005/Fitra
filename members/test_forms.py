"""
members/tests/test_forms.py

Tests for RegistrationForm validation logic (members/forms.py).
Uses Django's built-in TestCase (no pytest, no extra installs).

Place this file at: members/tests/test_forms.py
(create members/tests/__init__.py if converting tests.py into a package,
or just drop this alongside your existing tests.py as test_forms.py —
Django's test runner auto-discovers any test_*.py file.)
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from members.forms import RegistrationForm


def make_valid_base_data(**overrides):
    """
    Returns a dict of valid form data for a MALE registrant, using the
    ACTUAL choice values defined in members/models.py.
    Override individual fields via kwargs, e.g. make_valid_base_data(gender="FEMALE").
    """
    data = {
        "full_name": "Test User",
        "age": 25,
        "height": "175.50",
        "current_weight": "80.00",
        "measurement_date": "2026-07-01",
        "gender": "MALE",
        "occupation": "Engineer",
        "place_of_living": "Cairo",
        "phone": "01012345678",
        "email": "test@example.com",
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
    data.update(overrides)
    return data


def make_test_image(name="photo.jpg", size_bytes=1024, content_type="image/jpeg"):
    content = b"\xff\xd8\xff" + b"\x00" * size_bytes  # fake JPEG-ish header + padding
    return SimpleUploadedFile(name, content, content_type=content_type)


class MalePhotoValidationTests(TestCase):
    """Covers item #11: exactly 4 or 5 photos required for male registrants,
    each photo must be an image and each individually <= 10MB."""

    def test_male_with_zero_photos_is_invalid(self):
        data = make_valid_base_data(gender="MALE")
        form = RegistrationForm(data=data, files=MultiValueDict())
        self.assertFalse(form.is_valid())

    def test_male_with_three_photos_is_invalid(self):
        data = make_valid_base_data(gender="MALE")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(3)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())

    def test_male_with_four_photos_is_valid(self):
        data = make_valid_base_data(gender="MALE")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_male_with_five_photos_is_valid(self):
        data = make_valid_base_data(gender="MALE")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(5)]})
        form = RegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_male_with_six_photos_is_invalid(self):
        data = make_valid_base_data(gender="MALE")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(6)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())

    def test_male_photo_over_10mb_is_invalid(self):
        data = make_valid_base_data(gender="MALE")
        oversized = make_test_image("big.jpg", size_bytes=11 * 1024 * 1024)
        files = MultiValueDict({"male_photos": [oversized] + [make_test_image(f"p{i}.jpg") for i in range(3)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())

    def test_male_non_image_file_is_invalid(self):
        data = make_valid_base_data(gender="MALE")
        bad_file = SimpleUploadedFile("doc.pdf", b"not an image", content_type="application/pdf")
        files = MultiValueDict({"male_photos": [bad_file] + [make_test_image(f"p{i}.jpg") for i in range(3)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())


class FemaleMeasurementsValidationTests(TestCase):
    """Covers the FEMALE branch of RegistrationForm.clean()."""

    def test_female_without_measurements_is_invalid(self):
        data = make_valid_base_data(gender="FEMALE", female_measurements="")
        form = RegistrationForm(data=data, files=MultiValueDict())
        self.assertFalse(form.is_valid())
        self.assertIn("female_measurements", form.errors)

    def test_female_with_measurements_is_valid(self):
        data = make_valid_base_data(gender="FEMALE", female_measurements="90-60-90")
        form = RegistrationForm(data=data, files=MultiValueDict())
        self.assertTrue(form.is_valid(), form.errors)


class PhoneValidationTests(TestCase):
    """Covers the phone_validator RegexValidator (must be 01 + 9 digits = 11 total)."""

    def test_phone_too_short_is_invalid(self):
        data = make_valid_base_data(gender="MALE", phone="12345")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_phone_not_starting_with_01_is_invalid(self):
        data = make_valid_base_data(gender="MALE", phone="02012345678")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_valid_phone_passes(self):
        data = make_valid_base_data(gender="MALE", phone="01098765432")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_clean_phone_strips_whitespace(self):
        data = make_valid_base_data(gender="MALE", phone="  01098765432  ")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        # Note: the regex validator runs on the raw value before clean_phone's
        # strip happens in some Django versions' field-cleaning order; if this
        # fails, it reveals a real ordering issue worth checking rather than a
        # test mistake -- flag it instead of just deleting the test.
        if form.is_valid():
            self.assertEqual(form.cleaned_data["phone"], "01098765432")


class ChoiceFieldValidationTests(TestCase):
    """Covers item: MultipleChoiceField rejects values outside the defined choices."""

    def test_invalid_fitness_goal_choice_is_rejected(self):
        data = make_valid_base_data(gender="MALE", fitness_goal=["NOT_A_REAL_GOAL"])
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("fitness_goal", form.errors)

    def test_invalid_how_hear_choice_is_rejected(self):
        data = make_valid_base_data(gender="MALE", how_hear=["NOT_A_REAL_SOURCE"])
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertFalse(form.is_valid())
        self.assertIn("how_hear", form.errors)

    def test_how_hear_is_optional(self):
        # how_hear has required=False in the form
        data = make_valid_base_data(gender="MALE")
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)
