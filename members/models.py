from django.db import models
import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

GENDER = [
    ('MALE','Male'),
    ('FEMALE','Female'),
]

FITNESS_GOAL = [
    ('FAT LOSS','Fat loss'),
    ('INCREASE MUSCLE MASS','Increase muscle mass'),
    ('INCREASE STRENGTH','Increase strength'),
    ('INCREASE ENDURANCE','Increase endurance'),
    ('TRAIN FOR FUNCTIONALITY','Train for functionality'),
    ('HAVING FUN','Having fun'),
    ('POST REHABILITATION STRENGTH','Post rehabilitation strength'),
]

MEALS = [
    ('1 MEAL', '1 meal'),
    ('A MEAL','A meal'),
    ('2 MEALS','2 meals'),
    ('3 MEALS','3 meals'),
    ('4 MEALS','4 meals'),
    ('5 MEALS','5 meals'),
]

WORKOUT_DAYS = [
    ('A DAY','A day'),
    ('2 DAYS','2 days'),
    ('3 DAYS','3 days'),
    ('4 DAYS','4 days'),
    ('5 DAYS','5 days'),
    ('6 DAYS','6 days'),
]

TRAINING_TYPE = [
    ('GYM','Gym'),
    ('HOME','Home'),
]

PLAN = [
    ('DUOS','Duos'),
    ('EPIC','Epic'),
    ('LEGENDARY','Legendary'),
]

DAILY_SPENDING = [
    ('LESS THAN 100 BUCKS', 'Less than 100 bucks'),
    ('100-150 BUCKS','100-150 bucks'),
    ('150-200 BUCKS','150-200 bucks'),
    ('MORE THAN 200 BUCKS','More than 200 bucks'),
]

PREVIOUS_GYM = [
    ('YES','Yes'),
    ('NO','No'),
]

LIFESTYLE_COMMITMENT = [
    ('ABSOLUTELY','Absolutely'),
    ('MAYBE','Maybe'),
    ('NO','No'),
]

# Keep CONFIDENCE as an alias so existing import references in tests don't break immediately
CONFIDENCE = LIFESTYLE_COMMITMENT

COMEBACK = [
    ('ABSOLUTELY','Absolutely'),
    ('NO','No'),
]

HEAR_ABOUT_US = [
    ('A FRIEND','A friend'),
    ('FACEBOOK','Facebook'),
    ('INSTAGRAM','Instagram'),
    ('TIKTOK','Tiktok'),
    ('OTHER','Other'),
]

RECOMMEND_US = [
    (1,1),
    (2,2),
    (3,3),
    (4,4),
    (5,5),
]

GOVERNORATE = [
    ("Alexandria","Alexandria"),
    ("Aswan","Aswan"),
    ("Asyut","Asyut"),
    ('Beheira','Beheira'),
    ('Beni Suef','Beni Suef'),
    ("Cairo","Cairo"),
    ("Dakahlia","Dakahlia"),
    ("Damietta","Damietta"),
    ("Faiyum","Faiyum"),
    ("Gharbia","Gharbia"),
    ("Giza","Giza"),
    ("Ismailia","Ismailia"),
    ("Kafr El Sheikh","Kafr El Sheikh"),
    ("Luxor","Luxor"),
    ("Matruh","Matruh"),
    ("Minya","Minya"),
    ("Monufia","Monufia"),
    ("New Valley",'New Valley (Wadi El Gedid)'),
    ("North Sinai","North Sinai"),
    ("Port Said","Port Said"),
    ("Qalyubia","Qalyubia"),
    ("Qena","Qena"),
    ("Red Sea","Red Sea"),
    ("Sharqia","Sharqia"),
    ("Sohag","Sohag"),
    ("South Sinai","South Sinai"),
    ("Suez","Suez"),
]

TRAINING_AGE = [
    ('3 MONTHS', '3 months'),
    ('6 MONTHS', '6 months'),
    ('1 YEAR', '1 year'),
    ('2 YEARS', '2 years'),
    ('MORE THAN 2 YEARS', 'More than 2 years'),
    ('ON AND OFF', 'On and off'),
    ('NEVER TRAINED BEFORE', 'Never trained before'),
]

GYM_SETS_PER_WEEK = [
    ('2-4', '2-4'),
    ('4-6', '4-6'),
    ('6-8', '6-8'),
    ('8-12', '8-12'),
    ('12-15', '12-15'),
    ('15-20', '15-20'),
]

FAILURE_RIR = [
    ('YES I KNOW BOTH', 'Yes, I know both'),
    ('MUSCLE FAILURE ONLY', 'I know muscle failure only'),
    ('RIR ONLY', "I know RIR only, but can't quite apply it"),
    ('NEITHER', "I don't know either"),
]

GYM_BENCH_MOVE = [
    ('CAN MOVE', "It's fine, I can move it"),
    ('HARD TO MOVE', "No, it's hard to move"),
]

TRAINING_TIME = [
    ('MORNING', 'Morning'),
    ('MIDDAY', 'Midday'),
    ('NIGHT', 'Night'),
]

SESSION_DURATION = [
    ('1 HOUR', '1 hour'),
    ('1.5 HOURS', '1.5 hours'),
    ('2 HOURS', '2 hours'),
]

TRAINER_BEFORE = [
    ('YES', 'Yes'),
    ('NO', 'No'),
]


class Governorate(models.Model):
    governorate_name = models.CharField(verbose_name=_('Governorate name'), max_length=30, choices=GOVERNORATE, unique=True)
    def __str__(self):
        return self.governorate_name


class Member(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    firebase_uid = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )

    deadline = models.DateTimeField(
        null=True,
        blank=True,
    )

    account_status = models.BooleanField(
        default=True,
    )
    join_date = models.DateField(verbose_name=_('Join Date'), auto_now_add=True)
    name = models.CharField(verbose_name=_('Name'), max_length=60)
    age = models.PositiveSmallIntegerField(verbose_name=_('Age'))
    height = models.DecimalField(verbose_name=_('Height (cm)'), max_digits=5, decimal_places=2)
    weight = models.DecimalField(verbose_name=_('Weight (kg)'), max_digits=5, decimal_places=2)
    weight_measure_date = models.DateField(verbose_name=_('Weight Measurement Date'), default=datetime.date.today)
    whatsapp_number = models.CharField(verbose_name=_('Whatsapp Number'), max_length=13)
    email = models.EmailField(verbose_name=_('Email'), unique=True)
    email_confirmed = models.BooleanField(verbose_name='Email Confirmed', default=False)
    telegram_username = models.CharField(verbose_name=_('Telegram Username'), max_length=50, blank=True, null=True)
    place = models.ForeignKey(Governorate, on_delete=models.PROTECT, related_name='user_governorate')
    gender = models.CharField(verbose_name=_('Gender'), max_length=6, choices=GENDER)
    education = models.CharField(verbose_name=_('Education or Occupation'), max_length=150)
    sizes = models.TextField(null=True, blank=True)
    plan = models.CharField(verbose_name=_('Plan'), max_length=9, choices=PLAN)
    recommend_us = models.IntegerField(verbose_name=_('Recommend us'), choices=RECOMMEND_US)
    meals_num = models.CharField(verbose_name=_('Meals number'), max_length=7, choices=MEALS)
    training_type = models.CharField(verbose_name=_('Gym or home'), max_length=4, choices=TRAINING_TYPE)
    workout_days = models.CharField(verbose_name=_('Workout available days'), max_length=6, choices=WORKOUT_DAYS)
    daily_spend = models.CharField(verbose_name=_('Daily spending for food'), max_length=20, choices=DAILY_SPENDING)
    previous_gym = models.CharField(verbose_name=_('Previous gym'), max_length=3, choices=PREVIOUS_GYM)
    another_sports = models.TextField(verbose_name=_('Other Sports'), blank=True, null=True)
    habits = models.TextField(verbose_name=_('Any Habits'))
    lifestyle_commitment = models.CharField(verbose_name=_('Lifestyle Commitment'), max_length=10, choices=LIFESTYLE_COMMITMENT)
    comeback = models.CharField(verbose_name=_('Comeback'), max_length=10, choices=COMEBACK)
    is_activated = models.BooleanField(verbose_name='IS Activated', default=False)
    trainee_code = models.CharField(null=True, blank=True)
    preferred_language = models.CharField(verbose_name=_('Preferred Language'), max_length=5, default='en', choices=[('en', 'English'), ('ar', 'Arabic')])

    # ---------- New fields ----------
    training_age = models.CharField(
        verbose_name=_('Training Age'), max_length=20, choices=TRAINING_AGE, blank=True, null=True
    )
    gym_sets_per_week = models.CharField(
        verbose_name=_('Gym Sets Per Week'), max_length=5, choices=GYM_SETS_PER_WEEK, blank=True, null=True
    )
    failure_rir = models.CharField(
        verbose_name=_('Failure / RIR Knowledge'), max_length=20, choices=FAILURE_RIR, blank=True, null=True
    )
    gym_bench_move = models.CharField(
        verbose_name=_('Can Move Bench?'), max_length=12, choices=GYM_BENCH_MOVE, blank=True, null=True
    )
    training_time = models.CharField(
        verbose_name=_('Training Time'), max_length=7, choices=TRAINING_TIME, blank=True, null=True
    )
    session_duration = models.CharField(
        verbose_name=_('Session Duration'), max_length=10, choices=SESSION_DURATION, blank=True, null=True
    )
    daily_steps = models.CharField(
        verbose_name=_('Daily Steps'), max_length=20, blank=True, null=True
    )
    current_split = models.TextField(verbose_name=_('Current Training Split'), blank=True, null=True)
    goal_timeframe = models.TextField(verbose_name=_('Goal Timeframe'), blank=True, null=True)
    wanted_exercise = models.TextField(verbose_name=_('Wanted Exercise'), blank=True, null=True)
    unwanted_exercise = models.TextField(verbose_name=_('Unwanted Exercise'), blank=True, null=True)
    chronic_illness = models.TextField(verbose_name=_('Chronic Illness'), blank=True, null=True)
    injury_issue = models.TextField(verbose_name=_('Injury / Issue'), blank=True, null=True)
    medication = models.TextField(verbose_name=_('Medication'), blank=True, null=True)
    allergy = models.TextField(verbose_name=_('Allergy'), blank=True, null=True)
    breakfast = models.TextField(verbose_name=_('Breakfast'), blank=True, null=True)
    lunch = models.TextField(verbose_name=_('Lunch'), blank=True, null=True)
    dinner = models.TextField(verbose_name=_('Dinner'), blank=True, null=True)
    liked_food = models.TextField(verbose_name=_('Liked Food'), blank=True, null=True)
    disliked_food = models.TextField(verbose_name=_('Disliked Food'), blank=True, null=True)
    favorite_meal = models.TextField(verbose_name=_('Favorite Meal'), blank=True, null=True)
    snack_preference = models.TextField(verbose_name=_('Snack Preference'), blank=True, null=True)
    wanted_diet_food = models.TextField(verbose_name=_('Wanted Diet Food'), blank=True, null=True)
    daily_drinks = models.TextField(verbose_name=_('Daily Drinks'), blank=True, null=True)
    trainer_before = models.CharField(
        verbose_name=_('Trainer Before'), max_length=3, choices=TRAINER_BEFORE, blank=True, null=True
    )
    trainer_problem = models.TextField(verbose_name=_('Trainer Problem'), blank=True, null=True)
    subscribe_reason = models.TextField(verbose_name=_('Subscribe Reason'), blank=True, null=True)

    def __str__(self):
        return self.name


class Goals(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='user_goals')
    goal = models.CharField(verbose_name=_('Fitness Goal'), max_length=30, choices=FITNESS_GOAL)


class Picture(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='user_images')
    images = models.ImageField(verbose_name=_('images'), upload_to='members/', null=True, blank=True)


class HearAboutUs(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="hear_about_us"
    )
    source = models.CharField(
        max_length=20,
        choices=HEAR_ABOUT_US
    )

    def __str__(self):
        return f"{self.member.name} - {self.source}"


class PendingRegistration(models.Model):
    email = models.EmailField(db_index=True)
    preferred_language = models.CharField(max_length=5, default='en')
    form_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Set for Renewal path: the existing Member.id to update on activation
    renewal_target_member_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Pending: {self.email} ({self.created_at:%Y-%m-%d %H:%M})"


class PendingPicture(models.Model):
    pending_registration = models.ForeignKey(
        PendingRegistration,
        on_delete=models.CASCADE,
        related_name='pending_pictures',
    )
    image = models.ImageField(upload_to='pending/')

    def __str__(self):
        return f"PendingPicture for PendingRegistration #{self.pending_registration_id}"


class PendingMember(Member):
    class Meta:
        proxy = True
        verbose_name = "Pending Member"
        verbose_name_plural = "Pending Members"
