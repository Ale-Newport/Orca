# Generated by Django 5.1.2 on 2024-11-16 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0007_lesson_notes_alter_lesson_tutor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='notes',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='tutor',
            field=models.CharField(default='Unknown Tutor', max_length=100),
        ),
    ]
