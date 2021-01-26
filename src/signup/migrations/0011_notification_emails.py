from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('signup', '0010_auto_20200923_1103'),
	]

	operations = [
		migrations.AddField(
			model_name='organisation',
			name='billing_manager_message',
			field=models.TextField(help_text='Message sent to Billing Managers when someone signs up.', null=True),
		),
		migrations.AddField(
			model_name='organisation',
			name='institution_message',
			field=models.TextField(help_text='Message sent to institution when they sign up.', null=True),
		),
	]