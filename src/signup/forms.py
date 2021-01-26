from django import forms

from signup import models


class SignupStart(forms.Form):
	country = forms.ChoiceField()

	def __init__(self, *args, **kwargs):
		super(SignupStart, self).__init__(*args, **kwargs)

		self.fields['country'].choices = [
			[country.code, country.name] for country in models.Country.objects.all()
		]


class BandingForm(forms.Form):
	banding = forms.ChoiceField()

	def __init__(self, *args, **kwargs):
		self.bandings = kwargs.pop('bandings')
		super(BandingForm, self).__init__(*args, **kwargs)

		self.fields['banding'].choices = [
			[banding.pk, banding.name] for banding in self.bandings
		]


class SignUpForm(forms.ModelForm):
	class Meta:
		model = models.SignUp
		fields = (
			'first_name',
			'last_name',
			'email_address',
			'institution',
			'address',
			'post_code',
			'phone_number',
			'technical_contact',
			'existing_customer',
		)


class AccessLogForm(forms.ModelForm):
	class Meta:
		model = models.AccessLog
		fields = (
			'signup',
			'access_type',
			'date_stamp',
			'ip_range',
			'payment_handler',
		)

	def __init__(self, *args, **kwargs):
		self.request = kwargs.pop('request')
		super().__init__(*args, **kwargs)

	def save(self, commit=True):
		access_log = super(AccessLogForm, self).save(commit=False)
		access_log.user = self.request.user

		if commit:
			access_log.save()

		return access_log


