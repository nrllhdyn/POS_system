# Generated by Django 5.0.7 on 2024-08-06 00:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_staff_staff_unique_staff_per_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
