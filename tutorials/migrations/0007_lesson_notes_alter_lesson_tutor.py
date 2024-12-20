# Generated by Django 5.1.2 on 2024-11-16 18:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0006_remove_lesson_notes_alter_lesson_tutor'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tutored_lessons', to=settings.AUTH_USER_MODEL),
        ),
    ]
