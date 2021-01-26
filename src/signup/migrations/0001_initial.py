# Generated by Django 3.1.1 on 2020-09-14 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Banding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=9)),
                ('currency', models.CharField(help_text='Use the iso-4217 three digit currency code eg. GBP or USD', max_length=3)),
                ('redirect_url', models.URLField(blank=True, help_text='Can be used to overwrite the Country redirect.', null=True)),
                ('redirect', models.BooleanField(default=True, help_text='Disable this in order to ignore the redirect urls in thisobject OR at the country level.')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=4)),
                ('redirect_url', models.URLField(blank=True, help_text='If set once signup is complete the user will be redirected to this url.', null=True)),
            ],
            options={
                'verbose_name_plural': 'Countries',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(upload_to='')),
                ('hidden', models.BooleanField(default=False, help_text='If set this package wont be available for signup.')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='SignUp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email_address', models.CharField(max_length=200)),
                ('institution', models.CharField(max_length=200)),
                ('address', models.TextField(help_text='Please enter your billing address.')),
                ('post_code', models.CharField(max_length=10, verbose_name='Post/Zip Code')),
                ('technical_contact', models.TextField(help_text='Please enter details of a technical contact with whom we can discuss authentication methods.')),
                ('banding', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='signup.banding')),
            ],
            options={
                'ordering': ('institution',),
            },
        ),
        migrations.CreateModel(
            name='BillingManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Please enter Billing Managers full name.', max_length=300)),
                ('country', models.ForeignKey(help_text='Leave blank to be notified of all sign ups.', on_delete=django.db.models.deletion.CASCADE, to='signup.country')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='banding',
            name='country',
            field=models.ForeignKey(blank=True, help_text='If left blank this will be a default banding available for countries where no bandings are set.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='signup.country'),
        ),
    ]