from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import (
    GENDER, FITNESS_GOAL, MEALS, WORKOUT_DAYS, TRAINING_TYPE, PLAN,
    DAILY_SPENDING, MEAURMENT_SCALE, PREVIOUS_GYM, CONFIDENCE, COMEBACK,
    HEAR_ABOUT_US, RECOMMEND_US, GOVERNORATE,
)

phone_validator = RegexValidator(
    regex=r'^01\d{9}$',
    message=_('Phone number must start with 01 and consist of exactly 11 digits.')
)


class RegistrationForm(forms.Form):
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
    email = forms.EmailField(
        required=True,
        error_messages={
            'invalid': _('Please enter a valid email address.')
        }
    )
    telegram_user = forms.CharField(max_length=50, required=False)

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
    measuring_scale = forms.ChoiceField(
        choices=MEAURMENT_SCALE, 
        widget=forms.RadioSelect, 
        required=True,
        error_messages={
            'required': _('Please select if you have a measuring scale.')
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
    past_nutrition = forms.CharField(
        widget=forms.Textarea, 
        required=True,
        error_messages={
            'required': _('Please describe your past nutrition experience.')
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
    illness = forms.CharField(
        widget=forms.Textarea, 
        required=True,
        error_messages={
            'required': _('Please describe any illness or injury (or write "None").')
        }
    )
    other_sports = forms.CharField(widget=forms.Textarea, required=False)

    gym_before = forms.ChoiceField(
        choices=PREVIOUS_GYM, 
        widget=forms.RadioSelect, 
        required=True,
        error_messages={
            'required': _('Please answer if you have been to a gym before.')
        }
    )
    confidence = forms.ChoiceField(
        choices=CONFIDENCE, 
        widget=forms.RadioSelect, 
        required=True,
        error_messages={
            'required': _('Please select your confidence level.')
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
        required=False
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

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        return phone

    def clean(self):
        cleaned_data = super().clean()
        gender = cleaned_data.get('gender')

        if gender == 'MALE':
            photos = self.files.getlist('male_photos')

            if len(photos) < 4 or len(photos) > 5:
                self.add_error(None, _('Please upload 4 or 5 photos.'))
            else:
                total_size = 0
                for photo in photos:
                    if not photo.content_type.startswith('image/'):
                        self.add_error(None, _('The file "%(filename)s" is not a valid image.') % {'filename': photo.name})
                    total_size += photo.size

                if total_size > 10 * 1024 * 1024:  # 10 MB combined
                    self.add_error(None, _('The total size of all photos must not exceed 10 MB.'))

        elif gender == 'FEMALE':
            if not cleaned_data.get('female_measurements'):
                self.add_error('female_measurements', _('Please enter your measurements.'))

        return cleaned_data
