# Generated by Django 3.1.1 on 2020-12-08 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signup', '0025_auto_20201208_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='payment_handler',
            field=models.TextField(blank=True, null=True),
        ),
    ]