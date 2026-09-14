from typing import Any

from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import (
    GENDER, FITNESS_GOAL, MEALS, WORKOUT_DAYS, TRAINING_TYPE, PLAN,
    DAILY_SPENDING, PREVIOUS_GYM, LIFESTYLE_COMMITMENT, COMEBACK,
    HEAR_ABOUT_US, RECOMMEND_US, GOVERNORATE,
    TRAINING_AGE, GYM_SETS_PER_WEEK, FAILURE_RIR, GYM_BENCH_MOVE,
    TRAINING_TIME, SESSION_DURATION, TRAINER_BEFORE,
    Member,
)

phone_validator = RegexValidator(
    regex=r'^01\d{9}$',
    message=_('Phone number must start with 01 and consist of exactly 11 digits.')
)

REGISTRATION_TYPE_CHOICES = [
    ('New', _('New Registration')),
    ('Renewal', _('Renewal')),
]


class RegistrationForm(forms.Form):

    # ------------------------------------------------------------------ #
    # Registration type selector (top of form, drives all conditional logic)
    # ------------------------------------------------------------------ #
    registration_type = forms.ChoiceField(
        choices=REGISTRATION_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        initial='New',
        error_messages={
            'required': _('Please select a registration type.'),
        }
    )

    # ------------------------------------------------------------------ #
    # Renewal-only: existing member ID for lookup
    # ------------------------------------------------------------------ #
    member_id = forms.IntegerField(
        required=False,  # conditionally required in clean()
        min_value=1,
        error_messages={
            'invalid': _('Please enter a valid numeric Member ID.'),
            'min_value': _('Member ID must be a positive number.'),
        }
    )

    # ------------------------------------------------------------------ #
    # Personal information
    # ------------------------------------------------------------------ #
    full_name = forms.CharField(
        max_length=60,
        required=True,
        error_messages={
            'required': _('Please enter your full name.'),
            'max_length': _('Name is too long.')
        }
    )
    age = forms.IntegerField(
        min_value=10,
        max_value=100,
        required=True,
        error_messages={
            'required': _('Please enter your age.'),
            'invalid': _('Please enter a valid number.'),
            'min_value': _('Age must be at least 10.'),
            'max_value': _('Age cannot exceed 100.')
        }
    )
    height = forms.DecimalField(
        min_value=0,
        max_value=299.99,
        decimal_places=2,
        required=True,
        error_messages={
            'required': _('Please enter your height.'),
            'invalid': _('Please enter a valid number.'),
            'max_value': _('Height value is too large.')
        }
    )
    current_weight = forms.DecimalField(
        min_value=0,
        max_value=299.99,
        decimal_places=2,
        required=True,
        error_messages={
            'required': _('Please enter your current weight.'),
            'invalid': _('Please enter a valid number.'),
            'max_value': _('Weight value is too large.')
        }
    )
    measurement_date = forms.DateField(
        required=True,
        error_messages={
            'required': _('Please select the measurement date.'),
            'invalid': _('Please enter a valid date.')
        }
    )
    gender = forms.ChoiceField(
        choices=GENDER,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your gender.')
        }
    )
    female_measurements = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    occupation = forms.CharField(
        max_length=150,
        required=True,
        error_messages={
            'required': _('Please enter your occupation or academic year.'),
            'max_length': _('Text is too long.')
        }
    )
    place_of_living = forms.ChoiceField(
        choices=GOVERNORATE,
        required=True,
        error_messages={
            'required': _('Please select your place of living.')
        }
    )
    phone = forms.CharField(
        max_length=13,
        required=True,
        validators=[phone_validator],
        error_messages={
            'required': _('Please enter your phone number.')
        }
    )

    # ------------------------------------------------------------------ #
    # Contact — email is required for New, ignored for Renewal
    # ------------------------------------------------------------------ #
    email = forms.EmailField(
        required=False,  # conditional; enforced in clean()
        error_messages={
            'invalid': _('Please enter a valid email address.')
        }
    )
    telegram_user = forms.CharField(max_length=50, required=False)

    # ------------------------------------------------------------------ #
    # Goals and lifestyle
    # ------------------------------------------------------------------ #
    fitness_goal = forms.MultipleChoiceField(
        choices=FITNESS_GOAL,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={
            'required': _('Please select at least one fitness goal.')
        }
    )
    meals_per_day = forms.ChoiceField(
        choices=MEALS,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select number of meals per day.')
        }
    )
    food_budget = forms.ChoiceField(
        choices=DAILY_SPENDING,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your daily food budget.')
        }
    )
    workout_days = forms.ChoiceField(
        choices=WORKOUT_DAYS,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select available workout days.')
        }
    )
    training_location = forms.ChoiceField(
        choices=TRAINING_TYPE,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your training location.')
        }
    )
    habit = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please describe your daily or weekly habits.')
        }
    )
    plan_type = forms.ChoiceField(
        choices=PLAN,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your plan.')
        }
    )
    other_sports = forms.CharField(widget=forms.Textarea, required=False)

    # ------------------------------------------------------------------ #
    # Training background (conditionally required for New path)
    # ------------------------------------------------------------------ #
    gym_before = forms.ChoiceField(
        choices=PREVIOUS_GYM,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() for New path
        error_messages={
            'required': _('Please answer if you have been to a gym before.')
        }
    )
    training_age = forms.ChoiceField(
        choices=TRAINING_AGE,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() for New path
        error_messages={
            'required': _('Please select your training age.')
        }
    )
    gym_sets_per_week = forms.ChoiceField(
        choices=GYM_SETS_PER_WEEK,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() when gym_before == YES
        error_messages={
            'required': _('Please select how many sets per week you do.')
        }
    )
    failure_rir = forms.ChoiceField(
        choices=FAILURE_RIR,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() for New path
        error_messages={
            'required': _('Please select your failure/RIR knowledge level.')
        }
    )
    gym_bench_move = forms.ChoiceField(
        choices=GYM_BENCH_MOVE,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() when training_location == GYM
        error_messages={
            'required': _('Please answer if you can move the bench.')
        }
    )
    training_time = forms.ChoiceField(
        choices=TRAINING_TIME,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your preferred training time.')
        }
    )
    session_duration = forms.ChoiceField(
        choices=SESSION_DURATION,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your session duration.')
        }
    )
    daily_steps = forms.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': _('Please enter your approximate daily steps.')
        }
    )
    current_split = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please describe your current training split.')
        }
    )
    goal_timeframe = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please describe your goal timeframe.')
        }
    )
    wanted_exercise = forms.CharField(widget=forms.Textarea, required=False)
    unwanted_exercise = forms.CharField(widget=forms.Textarea, required=False)

    # ------------------------------------------------------------------ #
    # Health
    # ------------------------------------------------------------------ #
    chronic_illness = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please describe any chronic illness (or write "None").')
        }
    )
    injury_issue = forms.CharField(widget=forms.Textarea, required=False)
    medication = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please list any medication you take (or write "None").')
        }
    )
    allergy = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={
            'required': _('Please list any allergies (or write "None").')
        }
    )

    # ------------------------------------------------------------------ #
    # Nutrition details
    # ------------------------------------------------------------------ #
    breakfast = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe your typical breakfast.')}
    )
    lunch = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe your typical lunch.')}
    )
    dinner = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe your typical dinner.')}
    )
    liked_food = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please list foods you like.')}
    )
    disliked_food = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please list foods you dislike.')}
    )
    favorite_meal = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe your favorite meal.')}
    )
    snack_preference = forms.CharField(widget=forms.Textarea, required=False)
    wanted_diet_food = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe what diet food you want.')}
    )
    daily_drinks = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please describe your daily drinks.')}
    )

    # ------------------------------------------------------------------ #
    # Trainer history (conditionally required for New path)
    # ------------------------------------------------------------------ #
    trainer_before = forms.ChoiceField(
        choices=TRAINER_BEFORE,
        widget=forms.RadioSelect,
        required=False,  # enforced in clean() for New path
        error_messages={
            'required': _('Please answer if you have worked with a trainer before.')
        }
    )
    trainer_problem = forms.CharField(
        widget=forms.Textarea,
        required=False,  # enforced in clean() when trainer_before == YES
    )

    # ------------------------------------------------------------------ #
    # Motivation & feedback
    # ------------------------------------------------------------------ #
    subscribe_reason = forms.CharField(
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _('Please tell us why you want to subscribe.')}
    )
    lifestyle_commitment = forms.ChoiceField(
        choices=LIFESTYLE_COMMITMENT,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please select your lifestyle commitment level.')
        }
    )
    return_continuity = forms.ChoiceField(
        choices=COMEBACK,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please answer about your commitment.')
        }
    )
    how_hear = forms.MultipleChoiceField(
        choices=HEAR_ABOUT_US,
        widget=forms.CheckboxSelectMultiple,
        required=False,  # enforced in clean() for New path
    )
    recommendation_rating = forms.TypedChoiceField(
        choices=RECOMMEND_US,
        coerce=int,
        widget=forms.RadioSelect,
        required=True,
        error_messages={
            'required': _('Please rate how likely you would recommend us.')
        }
    )

    # ------------------------------------------------------------------ #
    # Terms and Conditions
    # ------------------------------------------------------------------ #
    terms_acceptance = forms.BooleanField(
        required=False,  # enforced in clean() with a clear custom message
        error_messages={
            'required': _('You must accept the terms and conditions to submit.')
        }
    )

    # ------------------------------------------------------------------ #
    # Field cleaners
    # ------------------------------------------------------------------ #
    def clean_phone(self) -> str:
        return self.cleaned_data['phone'].strip()

    def clean_member_id(self):
        """Validate member_id exists in DB when supplied (Renewal path check
        happens in clean() once we know registration_type)."""
        member_id = self.cleaned_data.get('member_id')
        if member_id is not None:
            if not Member.objects.filter(id=member_id).exists():
                raise forms.ValidationError(
                    _('No member found with that ID. Please check your Member ID.')
                )
        return member_id

    def clean(self) -> dict[str, Any]:
        cleaned_data: dict[str, Any] = super().clean()
        reg_type: str = cleaned_data.get('registration_type', 'New')

        # ---- Registration-type branching ---- #
        if reg_type == 'Renewal':
            # member_id is required
            if not cleaned_data.get('member_id'):
                self.add_error('member_id', _('Your existing Member ID is required for renewal.'))

            # Fields NOT required in Renewal path — clear any spurious errors
            # so the form still validates even if they were left empty.
            for field_name in (
                'gym_before', 'gym_sets_per_week', 'training_age',
                'failure_rir', 'trainer_before', 'trainer_problem', 'how_hear',
            ):
                self.fields[field_name].required = False
                # Remove validation errors added by the base field validators
                if field_name in self._errors:
                    del self._errors[field_name]
                    cleaned_data.setdefault(field_name, '' if field_name != 'how_hear' else [])

        else:  # 'New' path
            # email is required
            if not cleaned_data.get('email'):
                self.add_error('email', _('Please enter your email address.'))

            # Required fields for New path
            for field_name in ('gym_before', 'training_age', 'failure_rir', 'trainer_before'):
                if not cleaned_data.get(field_name):
                    self.add_error(
                        field_name,
                        self.fields[field_name].error_messages.get('required', _('This field is required.'))
                    )

            # gym_sets_per_week required only if gym_before == 'YES'
            if cleaned_data.get('gym_before') == 'YES' and not cleaned_data.get('gym_sets_per_week'):
                self.add_error('gym_sets_per_week', _('Please select how many sets per week you do at the gym.'))

            # trainer_problem required only if trainer_before == 'YES'
            if cleaned_data.get('trainer_before') == 'YES' and not cleaned_data.get('trainer_problem', '').strip():
                self.add_error('trainer_problem', _('Please describe any problem you had with your previous trainer.'))

        # ---- Conditional: gym_bench_move required when training at the gym ---- #
        if cleaned_data.get('training_location') == 'GYM' and not cleaned_data.get('gym_bench_move'):
            self.add_error('gym_bench_move', _('Please answer if you can move the gym bench.'))

        # ---- Terms and conditions ---- #
        if not cleaned_data.get('terms_acceptance'):
            self.add_error('terms_acceptance', _('You must accept the terms and conditions to submit.'))

        # ---- Gender-based validations (unchanged from original) ---- #
        gender: str | None = cleaned_data.get('gender')
        if gender == 'MALE':
            photos = self.files.getlist('male_photos')
            if len(photos) < 4 or len(photos) > 5:
                self.add_error(None, _('Please upload 4 or 5 photos.'))
            else:
                total_size: int = 0
                for photo in photos:
                    if not photo.content_type.startswith('image/'):
                        self.add_error(
                            None,
                            _('The file "%(filename)s" is not a valid image.') % {'filename': photo.name}
                        )
                    total_size += photo.size
                if total_size > 10 * 1024 * 1024:
                    self.add_error(None, _('The total size of all photos must not exceed 10 MB.'))

        elif gender == 'FEMALE':
            if not cleaned_data.get('female_measurements'):
                self.add_error('female_measurements', _('Please enter your measurements.'))

        return cleaned_data
