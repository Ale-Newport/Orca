# Generated by Django 5.1.2 on 2024-12-06 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutorials', '0022_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='name',
            field=models.CharField(choices=[('Python', 'Python'), ('Java', 'Java'), ('C++', 'C++'), ('Scala', 'Scala'), ('Web Development', 'Web Development')], max_length=100),
        ),
        migrations.DeleteModel(
            name='tutorRequest',
        ),
    ]
