# Generated by Django 4.2 on 2023-06-11 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bellatutors_web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='due_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
