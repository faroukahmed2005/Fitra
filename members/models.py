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
    ('RARE','Rare'),
    ('EPIC','Epic'),
    ('LEGENDARY','Legendary'),
]

DAILY_SPENDING = [
    ('LESS THAN 100 BUCKS', 'Less than 100 bucks'),
    ('100-150 BUCKS','100-150 bucks'),
    ('150-200 BUCKS','150-200 bucks'),
    ('MORE THAN 200 BUCKS','More then 200 bucks'),
]

MEASUREMENT_SCALE = [
    ('I DO HAVE','I do have'),
    ('I DO NOT HAVE','I do not have'),
    ('NO, BUT I WILL','No, but i will'),
]

PREVIOUS_GYM = [
    ('YES','Yes'),
    ('NO','No'),
]

CONFIDENCE = [
    ('ABSOLUTELY','Absolutely'),
    ('MAYBE','Maybe'),
    ('NO','No'),
]

COMEBACK = [
    ('ABSOLUTELY','Absolutely'),
    ('NOT SURE','Not sure'),
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
    weight_measure_date = models.DateField(verbose_name=_('Weight Measurement Date'), default= datetime.date.today)
    whatsapp_number = models.CharField(verbose_name=_('Whatsapp Number'), max_length=13)
    email = models.EmailField(verbose_name=_('Email'),unique=True)
    email_confirmed = models.BooleanField(verbose_name='Email Confirmed', default=False)
    telegram_username = models.CharField(verbose_name=_('Telegram Username'), max_length=50, blank=True, null=True)
    place = models.ForeignKey(Governorate,on_delete=models.PROTECT, related_name='user_governorate')
    gender = models.CharField(verbose_name=_('Gender'), max_length=6, choices=GENDER)
    education = models.CharField(verbose_name=_('Education or Occupation'), max_length=150)
    sizes = models.TextField(null=True, blank=True)
    plan = models.CharField(verbose_name=_('Plan'), max_length=9, choices=PLAN)
    recommend_us = models.IntegerField(verbose_name=_('Recommend us'), choices=RECOMMEND_US)
    meals_num = models.CharField(verbose_name=_('Meals number'), max_length=7, choices=MEALS)
    training_type = models.CharField(verbose_name=_('Gym or home'), max_length=4, choices=TRAINING_TYPE)
    workout_days = models.CharField(verbose_name=_('Workout available days'), max_length=6, choices=WORKOUT_DAYS)
    daily_spend = models.CharField(verbose_name=_('Daily spending for food '), max_length=20, choices=DAILY_SPENDING)
    measure_scale = models.CharField(verbose_name=_('Having measurement scale?'), max_length=15, choices=MEASUREMENT_SCALE)
    before_nutrition = models.TextField(verbose_name=_('Past Nutrition'))
    injuries = models.TextField(verbose_name=_('Injuries'))
    previous_gym = models.CharField(verbose_name=_('Previous gym'), max_length=3, choices=PREVIOUS_GYM)
    another_sports = models.TextField(verbose_name=_('Other Sports'), blank=True, null= True)
    habits = models.TextField(verbose_name=_('Any Habits'))
    confidence = models.CharField(verbose_name=_('Confidence'), max_length=10, choices=CONFIDENCE)
    comeback = models.CharField(verbose_name=_('Comeback'), max_length=10, choices=COMEBACK)
    is_activated = models.BooleanField(verbose_name=('IS Activated'), default=False)
    trainee_code = models.CharField(null=True, blank=True)
    preferred_language = models.CharField(verbose_name=_('Preferred Language'), max_length=5, default='en', choices=[('en', 'English'), ('ar', 'Arabic')])
    def __str__(self):
        return self.name

class Goals(models.Model):
    member = models.ForeignKey(Member,on_delete=models.CASCADE, related_name='user_goals')
    goal = models.CharField(verbose_name=_('Fitness Goal'), max_length=30, choices=FITNESS_GOAL)

class Picture(models.Model):
    member = models.ForeignKey(Member,on_delete=models.CASCADE, related_name='user_images')
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