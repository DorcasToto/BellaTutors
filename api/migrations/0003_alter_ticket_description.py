# Generated by Django 4.2 on 2024-01-06 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_ticket_ticket_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
