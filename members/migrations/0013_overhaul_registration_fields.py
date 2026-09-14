# Generated manually for registration overhaul
# Depends on: 0012_alter_goals_goal_alter_governorate_governorate_name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0012_alter_goals_goal_alter_governorate_governorate_name'),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # 1. Remove fields that no longer exist on Member
        # ------------------------------------------------------------------ #
        migrations.RemoveField(
            model_name='member',
            name='measure_scale',
        ),
        migrations.RemoveField(
            model_name='member',
            name='before_nutrition',
        ),
        migrations.RemoveField(
            model_name='member',
            name='injuries',
        ),

        # ------------------------------------------------------------------ #
        # 2. Rename confidence -> lifestyle_commitment
        # ------------------------------------------------------------------ #
        migrations.RenameField(
            model_name='member',
            old_name='confidence',
            new_name='lifestyle_commitment',
        ),

        # ------------------------------------------------------------------ #
        # 3. Update choices on altered existing fields
        # ------------------------------------------------------------------ #
        migrations.AlterField(
            model_name='member',
            name='lifestyle_commitment',
            field=models.CharField(
                choices=[
                    ('ABSOLUTELY', 'Absolutely'),
                    ('MAYBE', 'Maybe'),
                    ('NO', 'No'),
                ],
                max_length=10,
                verbose_name='Lifestyle Commitment',
            ),
        ),
        migrations.AlterField(
            model_name='member',
            name='comeback',
            field=models.CharField(
                choices=[
                    ('ABSOLUTELY', 'Absolutely'),
                    ('NO', 'No'),
                ],
                max_length=10,
                verbose_name='Comeback',
            ),
        ),
        migrations.AlterField(
            model_name='member',
            name='plan',
            field=models.CharField(
                choices=[
                    ('DUOS', 'Duos'),
                    ('EPIC', 'Epic'),
                    ('LEGENDARY', 'Legendary'),
                ],
                max_length=9,
                verbose_name='Plan',
            ),
        ),
        migrations.AlterField(
            model_name='member',
            name='meals_num',
            field=models.CharField(
                choices=[
                    ('1 MEAL', '1 meal'),
                    ('A MEAL', 'A meal'),
                    ('2 MEALS', '2 meals'),
                    ('3 MEALS', '3 meals'),
                    ('4 MEALS', '4 meals'),
                    ('5 MEALS', '5 meals'),
                ],
                max_length=7,
                verbose_name='Meals number',
            ),
        ),

        # ------------------------------------------------------------------ #
        # 4. Add new fields to Member
        # ------------------------------------------------------------------ #
        migrations.AddField(
            model_name='member',
            name='training_age',
            field=models.CharField(
                blank=True,
                choices=[
                    ('3 MONTHS', '3 months'),
                    ('6 MONTHS', '6 months'),
                    ('1 YEAR', '1 year'),
                    ('2 YEARS', '2 years'),
                    ('MORE THAN 2 YEARS', 'More than 2 years'),
                    ('ON AND OFF', 'On and off'),
                    ('NEVER TRAINED BEFORE', 'Never trained before'),
                ],
                max_length=20,
                null=True,
                verbose_name='Training Age',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='gym_sets_per_week',
            field=models.CharField(
                blank=True,
                choices=[
                    ('2-4', '2-4'),
                    ('4-6', '4-6'),
                    ('6-8', '6-8'),
                    ('8-12', '8-12'),
                    ('12-15', '12-15'),
                    ('15-20', '15-20'),
                ],
                max_length=5,
                null=True,
                verbose_name='Gym Sets Per Week',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='failure_rir',
            field=models.CharField(
                blank=True,
                choices=[
                    ('YES I KNOW BOTH', 'Yes, I know both'),
                    ('MUSCLE FAILURE ONLY', 'I know muscle failure only'),
                    ('RIR ONLY', "I know RIR only, but can't quite apply it"),
                    ('NEITHER', "I don't know either"),
                ],
                max_length=20,
                null=True,
                verbose_name='Failure / RIR Knowledge',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='gym_bench_move',
            field=models.CharField(
                blank=True,
                choices=[
                    ('CAN MOVE', "It's fine, I can move it"),
                    ('HARD TO MOVE', "No, it's hard to move"),
                ],
                max_length=12,
                null=True,
                verbose_name='Can Move Bench?',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='training_time',
            field=models.CharField(
                blank=True,
                choices=[
                    ('MORNING', 'Morning'),
                    ('MIDDAY', 'Midday'),
                    ('NIGHT', 'Night'),
                ],
                max_length=7,
                null=True,
                verbose_name='Training Time',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='session_duration',
            field=models.CharField(
                blank=True,
                choices=[
                    ('1 HOUR', '1 hour'),
                    ('1.5 HOURS', '1.5 hours'),
                    ('2 HOURS', '2 hours'),
                ],
                max_length=10,
                null=True,
                verbose_name='Session Duration',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='daily_steps',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Daily Steps'),
        ),
        migrations.AddField(
            model_name='member',
            name='current_split',
            field=models.TextField(blank=True, null=True, verbose_name='Current Training Split'),
        ),
        migrations.AddField(
            model_name='member',
            name='goal_timeframe',
            field=models.TextField(blank=True, null=True, verbose_name='Goal Timeframe'),
        ),
        migrations.AddField(
            model_name='member',
            name='wanted_exercise',
            field=models.TextField(blank=True, null=True, verbose_name='Wanted Exercise'),
        ),
        migrations.AddField(
            model_name='member',
            name='unwanted_exercise',
            field=models.TextField(blank=True, null=True, verbose_name='Unwanted Exercise'),
        ),
        migrations.AddField(
            model_name='member',
            name='chronic_illness',
            field=models.TextField(blank=True, null=True, verbose_name='Chronic Illness'),
        ),
        migrations.AddField(
            model_name='member',
            name='injury_issue',
            field=models.TextField(blank=True, null=True, verbose_name='Injury / Issue'),
        ),
        migrations.AddField(
            model_name='member',
            name='medication',
            field=models.TextField(blank=True, null=True, verbose_name='Medication'),
        ),
        migrations.AddField(
            model_name='member',
            name='allergy',
            field=models.TextField(blank=True, null=True, verbose_name='Allergy'),
        ),
        migrations.AddField(
            model_name='member',
            name='breakfast',
            field=models.TextField(blank=True, null=True, verbose_name='Breakfast'),
        ),
        migrations.AddField(
            model_name='member',
            name='lunch',
            field=models.TextField(blank=True, null=True, verbose_name='Lunch'),
        ),
        migrations.AddField(
            model_name='member',
            name='dinner',
            field=models.TextField(blank=True, null=True, verbose_name='Dinner'),
        ),
        migrations.AddField(
            model_name='member',
            name='liked_food',
            field=models.TextField(blank=True, null=True, verbose_name='Liked Food'),
        ),
        migrations.AddField(
            model_name='member',
            name='disliked_food',
            field=models.TextField(blank=True, null=True, verbose_name='Disliked Food'),
        ),
        migrations.AddField(
            model_name='member',
            name='favorite_meal',
            field=models.TextField(blank=True, null=True, verbose_name='Favorite Meal'),
        ),
        migrations.AddField(
            model_name='member',
            name='snack_preference',
            field=models.TextField(blank=True, null=True, verbose_name='Snack Preference'),
        ),
        migrations.AddField(
            model_name='member',
            name='wanted_diet_food',
            field=models.TextField(blank=True, null=True, verbose_name='Wanted Diet Food'),
        ),
        migrations.AddField(
            model_name='member',
            name='daily_drinks',
            field=models.TextField(blank=True, null=True, verbose_name='Daily Drinks'),
        ),
        migrations.AddField(
            model_name='member',
            name='trainer_before',
            field=models.CharField(
                blank=True,
                choices=[('YES', 'Yes'), ('NO', 'No')],
                max_length=3,
                null=True,
                verbose_name='Trainer Before',
            ),
        ),
        migrations.AddField(
            model_name='member',
            name='trainer_problem',
            field=models.TextField(blank=True, null=True, verbose_name='Trainer Problem'),
        ),
        migrations.AddField(
            model_name='member',
            name='subscribe_reason',
            field=models.TextField(blank=True, null=True, verbose_name='Subscribe Reason'),
        ),

        # ------------------------------------------------------------------ #
        # 5. Add renewal_target_member_id to PendingRegistration
        # ------------------------------------------------------------------ #
        migrations.AddField(
            model_name='pendingregistration',
            name='renewal_target_member_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
