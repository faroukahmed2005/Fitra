"""
members/test_forms.py

Tests for RegistrationForm validation logic (members/forms.py).

Updated for the registration overhaul:
- registration_type (New/Renewal) field added
- confidence -> lifestyle_commitment
- illness -> chronic_illness + injury_issue
- measuring_scale field removed
- past_nutrition field removed
- plan_type RARE -> DUOS
- return_continuity choices: NOT SURE -> NO
- meals_per_day: '1 MEAL' option added
- terms_acceptance required
- New fields: training_age, failure_rir, gym_bench_move, training_time,
  session_duration, daily_steps, current_split, goal_timeframe, trainer_before,
  chronic_illness, medication, allergy, breakfast, lunch, dinner, liked_food,
  disliked_food, favorite_meal, wanted_diet_food, daily_drinks, subscribe_reason
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.datastructures import MultiValueDict
from members.forms import RegistrationForm


def make_valid_base_data(**overrides):
    """
    Returns a dict of valid form data for a MALE New registrant.
    Override individual fields via kwargs.
    """
    data = {
        # Registration type
        "registration_type": "New",
        # Personal
        "full_name": "Test User",
        "age": 25,
        "height": "175.50",
        "current_weight": "80.00",
        "measurement_date": "2026-07-01",
        "gender": "MALE",
        "occupation": "Engineer",
        "place_of_living": "Cairo",
        # Contact
        "phone": "01012345678",
        "email": "test@example.com",
        # Goals
        "fitness_goal": ["FAT LOSS"],
        "meals_per_day": "3 MEALS",
        "food_budget": "100-150 BUCKS",
        "workout_days": "3 DAYS",
        "training_location": "GYM",
        "training_time": "MORNING",
        "session_duration": "1 HOUR",
        "daily_steps": "5000",
        "current_split": "Push Pull Legs",
        "goal_timeframe": "Lose 5 kg in 2 months",
        "habit": "Normal daily routine.",
        "plan_type": "DUOS",
        # Training background (New path)
        "gym_before": "YES",
        "gym_sets_per_week": "6-8",
        "training_age": "1 YEAR",
        "failure_rir": "YES I KNOW BOTH",
        "gym_bench_move": "CAN MOVE",
        "trainer_before": "NO",
        # Health
        "chronic_illness": "None",
        "medication": "None",
        "allergy": "None",
        # Nutrition
        "breakfast": "Eggs and oats",
        "lunch": "Rice and chicken",
        "dinner": "Salad",
        "liked_food": "Chicken",
        "disliked_food": "Fish",
        "favorite_meal": "Chicken shawarma",
        "wanted_diet_food": "High protein",
        "daily_drinks": "Water, coffee",
        # Motivation
        "subscribe_reason": "Want to get fit",
        "lifestyle_commitment": "ABSOLUTELY",
        "return_continuity": "ABSOLUTELY",
        "recommendation_rating": 5,
        # Terms
        "terms_acceptance": True,
    }
    data.update(overrides)
    return data


def make_test_image(name="photo.jpg", size_bytes=1024, content_type="image/jpeg"):
    content = b"\xff\xd8\xff" + b"\x00" * size_bytes
    return SimpleUploadedFile(name, content, content_type=content_type)


class MalePhotoValidationTests(TestCase):
    """4 or 5 photos required for male New registrants."""

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
    """FEMALE branch of RegistrationForm.clean()."""

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
    """phone_validator must be 01 + 9 digits = 11 total."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_phone_too_short_is_invalid(self):
        data = make_valid_base_data(phone="12345")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_phone_not_starting_with_01_is_invalid(self):
        data = make_valid_base_data(phone="02012345678")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_valid_phone_passes(self):
        data = make_valid_base_data(phone="01098765432")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_clean_phone_strips_whitespace(self):
        data = make_valid_base_data(phone="  01098765432  ")
        form = RegistrationForm(data=data, files=self._make_files())
        if form.is_valid():
            self.assertEqual(form.cleaned_data["phone"], "01098765432")


class ChoiceFieldValidationTests(TestCase):
    """MultipleChoiceField rejects values outside defined choices."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_invalid_fitness_goal_choice_is_rejected(self):
        data = make_valid_base_data(fitness_goal=["NOT_A_REAL_GOAL"])
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("fitness_goal", form.errors)

    def test_invalid_how_hear_choice_is_rejected(self):
        data = make_valid_base_data(how_hear=["NOT_A_REAL_SOURCE"])
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("how_hear", form.errors)

    def test_how_hear_is_optional(self):
        data = make_valid_base_data()
        # how_hear omitted entirely — should not cause a validation error
        data.pop("how_hear", None)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)


class TermsAcceptanceTests(TestCase):
    """terms_acceptance must be True to submit."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_missing_terms_is_invalid(self):
        data = make_valid_base_data()
        data.pop("terms_acceptance", None)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("terms_acceptance", form.errors)

    def test_false_terms_is_invalid(self):
        data = make_valid_base_data(terms_acceptance=False)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())

    def test_accepted_terms_passes(self):
        data = make_valid_base_data(terms_acceptance=True)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)


class PlanChoiceTests(TestCase):
    """Plan choices: DUOS, EPIC, LEGENDARY (RARE removed)."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_plan_duos_is_valid(self):
        data = make_valid_base_data(plan_type="DUOS")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_plan_epic_is_valid(self):
        data = make_valid_base_data(plan_type="EPIC")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_plan_legendary_is_valid(self):
        data = make_valid_base_data(plan_type="LEGENDARY")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_plan_rare_is_rejected(self):
        """RARE is no longer a valid plan choice."""
        data = make_valid_base_data(plan_type="RARE")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("plan_type", form.errors)


class ReturnContinuityChoiceTests(TestCase):
    """return_continuity choices: ABSOLUTELY and NO (NOT SURE removed)."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_return_continuity_no_is_valid(self):
        data = make_valid_base_data(return_continuity="NO")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_return_continuity_not_sure_is_rejected(self):
        """NOT SURE is no longer a valid choice."""
        data = make_valid_base_data(return_continuity="NOT SURE")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("return_continuity", form.errors)


class RenewalPathTests(TestCase):
    """Renewal registration type: member_id required, email not required."""

    def setUp(self):
        from members.models import Governorate, Member
        gov, _ = Governorate.objects.get_or_create(governorate_name="Cairo")
        self.existing_member = Member.objects.create(
            name="Existing User",
            age=30,
            height="175.00",
            weight="80.00",
            gender="MALE",
            education="Engineer",
            place=gov,
            whatsapp_number="01012345678",
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
        )

    def _renewal_data(self, **overrides):
        data = make_valid_base_data(
            registration_type="Renewal",
            member_id=self.existing_member.id,
        )
        # email not required for renewal — remove it to test
        data.pop("email", None)
        # training background fields not required for renewal
        data.pop("gym_before", None)
        data.pop("training_age", None)
        data.pop("failure_rir", None)
        data.pop("trainer_before", None)
        data.pop("gym_sets_per_week", None)
        data.update(overrides)
        return data

    def test_renewal_without_email_is_valid(self):
        data = self._renewal_data()
        files = MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})
        form = RegistrationForm(data=data, files=files)
        self.assertTrue(form.is_valid(), form.errors)

    def test_renewal_without_member_id_is_invalid(self):
        data = self._renewal_data()
        data.pop("member_id", None)
        form = RegistrationForm(data=data, files=MultiValueDict(
            {"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]}
        ))
        self.assertFalse(form.is_valid())
        self.assertIn("member_id", form.errors)

    def test_renewal_with_nonexistent_member_id_is_invalid(self):
        data = self._renewal_data(member_id=999999)
        form = RegistrationForm(data=data, files=MultiValueDict(
            {"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]}
        ))
        self.assertFalse(form.is_valid())
        self.assertIn("member_id", form.errors)


class GymBenchMoveConditionalTests(TestCase):
    """gym_bench_move required only when training_location == GYM."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_gym_location_without_bench_move_is_invalid(self):
        data = make_valid_base_data(training_location="GYM")
        data.pop("gym_bench_move", None)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("gym_bench_move", form.errors)

    def test_home_location_without_bench_move_is_valid(self):
        data = make_valid_base_data(training_location="HOME")
        data.pop("gym_bench_move", None)
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)


class TrainerProblemConditionalTests(TestCase):
    """trainer_problem required only when trainer_before == YES."""

    def _make_files(self):
        return MultiValueDict({"male_photos": [make_test_image(f"p{i}.jpg") for i in range(4)]})

    def test_trainer_yes_without_problem_is_invalid(self):
        data = make_valid_base_data(trainer_before="YES", trainer_problem="")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertFalse(form.is_valid())
        self.assertIn("trainer_problem", form.errors)

    def test_trainer_yes_with_problem_is_valid(self):
        data = make_valid_base_data(trainer_before="YES", trainer_problem="Didn't show up")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)

    def test_trainer_no_without_problem_is_valid(self):
        data = make_valid_base_data(trainer_before="NO", trainer_problem="")
        form = RegistrationForm(data=data, files=self._make_files())
        self.assertTrue(form.is_valid(), form.errors)
