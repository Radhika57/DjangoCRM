# Generated by Django 5.1 on 2025-06-12 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_remove_agent_activity_pin_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='prescription',
            name='ndc',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
