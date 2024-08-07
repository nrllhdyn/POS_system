# Generated by Django 5.0.7 on 2024-08-07 14:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_floor_options_alter_floor_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ['floor__name', 'number'], 'verbose_name': 'Table', 'verbose_name_plural': 'Tables'},
        ),
        migrations.AlterField(
            model_name='table',
            name='capacity',
            field=models.IntegerField(verbose_name='Capacity'),
        ),
        migrations.AlterField(
            model_name='table',
            name='floor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='core.floor', verbose_name='Floor'),
        ),
        migrations.AlterField(
            model_name='table',
            name='number',
            field=models.IntegerField(verbose_name='Table Number'),
        ),
        migrations.AlterField(
            model_name='table',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('occupied', 'Occupied')], default='available', max_length=10, verbose_name='Status'),
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together={('floor', 'number')},
        ),
    ]
