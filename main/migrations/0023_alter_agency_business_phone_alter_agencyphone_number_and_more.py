# Generated by Django 5.1 on 2025-05-26 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_agent_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='business_phone',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='agencyphone',
            name='number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='agentphone',
            name='number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='carrierphone',
            name='number',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
