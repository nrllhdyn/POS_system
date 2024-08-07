# Generated by Django 5.0.7 on 2024-08-07 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_restaurant_options_alter_stock_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='floor',
            options={'ordering': ['restaurant', 'name'], 'verbose_name': 'Floor', 'verbose_name_plural': 'Floors'},
        ),
        migrations.AlterField(
            model_name='floor',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Floor Name'),
        ),
        migrations.AlterField(
            model_name='floor',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='floors', to='core.restaurant', verbose_name='Restaurant'),
        ),
        migrations.AlterUniqueTogether(
            name='floor',
            unique_together={('restaurant', 'name')},
        ),
    ]
