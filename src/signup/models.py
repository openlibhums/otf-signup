from uuid import uuid4

from django.db import models
from django.db.models import Q
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Template, Context
from django.template.defaultfilters import linebreaksbr
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User


class Package(models.Model):
	organisation = models.ForeignKey(
		'Organisation',
		on_delete=models.CASCADE,
		null=True,
	)
	name = models.CharField(
		max_length=300,
	)
	description = models.TextField(
		blank=True,
		null=True,
	)
	image = models.ImageField()
	hidden = models.BooleanField(
		default=False,
		help_text="If set this package wont be available for signup.",
	)
	front_page = models.BooleanField(
		default=False,
		help_text="If enabled, this package will display on the homepage.",
	)
	items = models.TextField(
		null=True,
		help_text='Items available in this package. We recommend using a ordered'
				  'or unordered list.',
	)
	order = models.PositiveIntegerField(
		default=0,
	)

	class Meta:
		ordering = ('order', 'name',)

	def __str__(self):
		return self.name


class Country(models.Model):
	name = models.CharField(
		max_length=50,
	)
	code = models.CharField(
		max_length=4,
	)
	redirect_url = models.URLField(
		blank=True,
		null=True,
		help_text="If set once signup is complete the user will be redirected "
				  "to this url.",
	)

	class Meta:
		verbose_name_plural = 'Countries'
		ordering = ('name',)

	def __str__(self):
		return self.name


class Banding(models.Model):
	organisation = models.ForeignKey(
		'Organisation',
		on_delete=models.CASCADE,
		null=True,
	)
	name = models.CharField(
		max_length=300,
	)
	description = models.TextField(
		blank=True,
		null=True,
	)
	price = models.DecimalField(
		max_digits=9,
		decimal_places=2,
	)
	currency = models.CharField(
		max_length=3,
		help_text='Use the iso-4217 three digit currency code eg. GBP or USD',
	)
	country = models.ForeignKey(
		Country,
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		help_text="If left blank this will be a default banding available for "
				  "countries where no bandings are set.",
	)
	redirect_url = models.URLField(
		blank=True,
		null=True,
		help_text="Can be used to overwrite the Country redirect.",
	)
	redirect = models.BooleanField(
		default=True,
		help_text="Disable this in order to ignore the redirect urls in this"
				  "object OR at the country level.",
	)

	class Meta:
		ordering = ('price', 'name')

	def __str__(self):
		return '{name} {price}{currency}'.format(
			name=self.name,
			price=self.price,
			currency=self.currency,
		)


class SignUp(models.Model):
	first_name = models.CharField(
		max_length=50,
	)
	last_name = models.CharField(
		max_length=50,
	)
	email_address = models.EmailField(
		max_length=200,
	)
	institution = models.CharField(
		max_length=200,
	)
	phone_number = models.CharField(
		max_length=200,
		blank=True,
		null=True,
		help_text='Optional',
	)
	address = models.TextField(
		help_text="Please enter your billing address.",
	)
	post_code = models.CharField(
		max_length=10,
		verbose_name="Post/Zip Code",
	)
	banding = models.ForeignKey(
		Banding,
		on_delete=models.PROTECT,
	)
	package = models.ForeignKey(
		Package,
		null=True,
		on_delete=models.PROTECT,
	)
	technical_contact = models.TextField(
		help_text="Please enter details of a technical contact with whom we "
				  "can discuss authentication methods.",
	)
	existing_customer = models.BooleanField(
		default=False,
		verbose_name='Customer in the last three years?',
	)

	class Meta:
		ordering = ('institution',)

	def __str__(self):
		return self.institution

	def process_complete(self, organisation, banding, package):
		self.banding = banding
		self.package = package
		self.save()

		context = {
			'organisation': organisation,
			'banding': banding,
			'package': package,
			'signup': self,
		}

		self.send_signup_acknowledgement(context)
		self.send_billing_notifications(context)

	def render_email(self, context, template_text):
		template = Template(template_text)
		context['PRIMARY_BASE_DOMAIN'] = settings.PRIMARY_BASE_DOMAIN
		html_content = template.render(Context(context))
		return linebreaksbr(html_content)

	def send_email(self, to, subject, html):
		if not type(to) in [list, tuple]:
			to = [to]

		msg = EmailMultiAlternatives(
			subject,
			strip_tags(html),
			settings.FROM_ADDRESS,
			to,
		)
		msg.attach_alternative(html, "text/html")
		return msg.send()

	def send_signup_acknowledgement(self, context):
		rendered_template = self.render_email(
			context,
			context.get('organisation').institution_message,
		)
		self.send_email(
			self.email_address,
			'Thank you for your pledge',
			rendered_template,
		)

	def send_billing_notifications(self, context):
		organisation = context.get('organisation')
		rendered_template = self.render_email(
			context,
			organisation.billing_manager_message,
		)
		banding = context.get('banding')

		billing_managers = Contact.objects.filter(
			Q(country__isnull=True) | Q(country=banding.country),
			contact_type='billing',
			organisation=organisation,
		)

		for billing_manager in billing_managers:
			self.send_email(
				billing_manager.email,
				'New pledge',
				rendered_template,
			)

	def current_access_status(self):
		return self.accesslog_set.first()

	def admin_action_button(self):
		access_logs = self.accesslog_set.all()

		if access_logs.exists():
			if access_logs.first().access_type == 'revoke':
				return 'grant'
			else:
				return 'revoke'

		return 'grant'


class Contact(models.Model):
	organisation = models.ForeignKey(
		'Organisation',
		on_delete=models.CASCADE,
	)
	name = models.CharField(
		max_length=300,
		help_text="Please enter Billing Managers full name.",
	)
	country = models.ForeignKey(
		Country,
		on_delete=models.CASCADE,
		help_text="Leave blank to be notified of all sign ups.",
		blank=True,
		null=True,
	)
	email = models.EmailField(
		max_length=255,
	)
	contact_type = models.CharField(
		max_length=20,
		choices=(
			('billing', 'Billing'),
			('access', 'Access'),
		),
		default='billing',
	)

	class Meta:
		ordering = ('name',)

	def __str__(self):
		return self.name

	def send_access_message(self, access_log):
		context = {
			'organisation': self.organisation,
			'contact': self,
		}
		message = self.organisation.access_manager_message

		html = access_log.signup.render_email(context, message)
		access_log.signup.send_email(
			self.email,
			'Access Control Update',
			html,
		)


class Organisation(models.Model):
	name = models.CharField(
		max_length=300,
		help_text='The name of the organisation running this site.',
	)
	domain = models.CharField(
		max_length=300,
		default='localhost',
		help_text='The domain for this organisation',
	)
	image = models.ImageField(
		null=True,
	)
	address_one = models.CharField(
		max_length=300,
	)
	address_two = models.CharField(
		max_length=300,
	)
	post_code = models.CharField(
		max_length=20,
		help_text='Post or Zip Code',
	)
	phone_number = models.CharField(
		blank=True,
		null=True,
		max_length=30,
	)

	main_page_hero_text = models.CharField(
		null=True,
		max_length=300,
		help_text='Hero text that appears on the home page directly under '
				  'the nav bar.',
	)

	hero_card_one_title = models.CharField(
		null=True,
		max_length=300,
	)
	hero_card_one_text = models.TextField(
		null=True,
	)
	hero_card_one_image = models.ImageField()

	hero_card_two_title = models.CharField(
		null=True,
		max_length=300,
	)
	hero_card_two_text = models.TextField(
		null=True,
	)
	hero_card_two_image = models.ImageField()

	hero_card_three_title = models.CharField(
		null=True,
		max_length=300,
	)
	hero_card_three_text = models.TextField(
		null=True,
	)
	hero_card_three_image = models.ImageField()

	copyright_notice = models.CharField(
		null=True,
		max_length=300,
		help_text='Appears in the footer below links and such',
	)

	contact_email = models.EmailField(
		null=True,
		help_text='This email address will be used for the contact form.',
	)

	twitter_url = models.URLField(
		blank=True,
		null=True,
		max_length=100,
		help_text='Enter the full account url eg. '
				  'https://twitter.com/openlibhums',
	)

	about = models.TextField(
		null=True,
		help_text='The contents of this field will display '
				  'on the about page.',
	)
	privacy = models.TextField(
		null=True,
		help_text='The contents of this field will display '
				  'on the privacy page.',
	)
	billing_manager_message = models.TextField(
		null=True,
		help_text="Message sent to Billing Managers when someone signs up.",
	)
	institution_message = models.TextField(
		null=True,
		help_text="Message sent to institution when they sign up.",
	)
	access_manager_message = models.TextField(
		help_text='Message send to Access Managers when access is changed.',
		default='{{organisation.name}}\'s access controls have been updated.',
	)
	FAQ = models.TextField(
		null=True,
		blank=True,
		help_text='If the Display FAQ setting is enabled this page will'
				  ' display in the nav and site.',
	)
	display_faq = models.BooleanField(
		default=False,
		help_text='If enabled the FAQ page will display.',
	)
	resources = models.TextField(
		null=True,
		blank=True,
		help_text='If the Display Resources setting is enabled this page will'
				  ' display in the nav and site.',
	)
	display_resources = models.BooleanField(
		default=False,
		help_text='If enabled the Resources page will display.',
	)
	analytics_code = models.TextField(
		blank=True,
		null=True,
		help_text='Add all required JS here.',
	)

	def __str__(self):
		return self.name


class Resource(models.Model):
	organisation = models.ForeignKey(
		Organisation,
		on_delete=models.CASCADE,
	)
	file = models.FileField()
	title = models.CharField(
		max_length=255,
	)
	order = models.PositiveIntegerField()

	class Meta:
		ordering = ('order', 'title')

	def __str__(self):
		return self.file.name


class NewsItem(models.Model):
	organisation = models.ForeignKey(
		Organisation,
		on_delete=models.CASCADE,
	)
	title = models.CharField(
		max_length=500,
	)
	body = models.TextField()
	posted = models.DateTimeField(
		default=timezone.now,
	)
	posted_by = models.ForeignKey(
		User,
		blank=True,
		null=True,
		on_delete=models.SET_NULL,
	)
	image = models.ImageField()

	class Meta:
		ordering = ('-posted', 'title')

	def __str__(self):
		return self.title


def access_choices():
	return (
		('grant', 'Grant'),
		('revoke', 'Revoke'),
	)


class AccessLog(models.Model):
	signup = models.ForeignKey(
		SignUp,
		on_delete=models.CASCADE,
	)
	access_type = models.CharField(
		choices=access_choices(),
		max_length=10,
	)
	date_stamp = models.DateTimeField(
		default=timezone.now,
	)
	ip_range = models.TextField(
		blank=True,
		null=True,
	)
	user = models.ForeignKey(
		User,
		blank=True,
		null=True,
		on_delete=models.SET_NULL,
	)
	payment_handler = models.TextField(
		blank=True,
		null=True,
	)

	class Meta:
		ordering = ('-date_stamp',)

	def __str__(self):
		return '{} {}'.format(
			self.access_type,
			self.date_stamp,
		)


class AccessLogExportCode(models.Model):
	organisation = models.ForeignKey(
		'Organisation',
		default=1,
		on_delete=models.CASCADE,
	)
	issued_to = models.CharField(max_length=255)
	uuid = models.UUIDField(default=uuid4)
	active = models.BooleanField(default=True)

	class Meta:
		ordering = ('-active',)


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=AccessLog)
def send_access_update_message(sender, instance, created, **kwargs):
	if created:
		access_managers = Contact.objects.filter(
			contact_type='access',
			organisation=instance.signup.package.organisation,
		)

		for manager in access_managers:
			manager.send_access_message(instance)