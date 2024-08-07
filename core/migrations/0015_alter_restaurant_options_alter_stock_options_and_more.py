# Generated by Django 5.0.7 on 2024-08-07 13:42

import django.core.validators
import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_incomeexpense_staff'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='restaurant',
            options={'ordering': ['name'], 'verbose_name': 'Restaurant', 'verbose_name_plural': 'Restaurants'},
        ),
        migrations.AlterModelOptions(
            name='stock',
            options={'ordering': ['restaurant', 'menu_item__name'], 'verbose_name': 'Stock Item', 'verbose_name_plural': 'Stock Items'},
        ),
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ['floor__name', 'number']},
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='address',
            field=models.TextField(verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Restaurant Name'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='restaurants', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='owner_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='Owner Phone'),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_phone',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='Restaurant Phone'),
        ),
        migrations.AlterField(
            model_name='stock',
            name='warning_threshold',
            field=models.PositiveIntegerField(default=10, help_text='Minimum stock level to trigger a warning.', validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]