from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0006_alter_governorate_governorate_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PendingRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(db_index=True, max_length=254)),
                ('preferred_language', models.CharField(default='en', max_length=5)),
                ('form_data', models.JSONField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='PendingPicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='pending/')),
                ('pending_registration', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='pending_pictures',
                    to='members.pendingregistration',
                )),
            ],
        ),
    ]
