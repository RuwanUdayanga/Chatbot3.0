# Generated by Django 4.2.4 on 2023-08-11 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medibot', '0002_doctor_availability_day'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='doctor',
            name='id',
        ),
        migrations.AlterField(
            model_name='doctor',
            name='doctor_id',
            field=models.CharField(max_length=15, primary_key=True, serialize=False),
        ),
    ]
