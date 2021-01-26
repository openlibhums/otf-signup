from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import reverse

from django_summernote.admin import SummernoteModelAdmin

from signup import models, forms


class PackageAdmin(SummernoteModelAdmin):
	list_display = (
		'name',
		'hidden',
		'order',
	)
	list_filter = (
		'hidden',
	)
	search_fields = (
		'name',
	)
	summernote_fields = (
		'items',
	)


class CountryAdmin(SummernoteModelAdmin):
	list_display = (
		'name',
		'code',
		'redirect_url',
	)
	search_fields = (
		'name',
		'code',
	)


class BandingAdmin(SummernoteModelAdmin):
	list_display = (
		'name',
		'price',
		'currency',
		'country',
	)
	list_filter = (
		'country',
		'redirect',
	)
	raw_id_fields = (
		'country',
	)
	search_fields = (
		'name',
		'currency',
	)


class SignUpAdmin(SummernoteModelAdmin):
	list_display = (
		'pk',
		'institution',
		'package',
		'banding',
		'first_name',
		'last_name',
		'email_address',
		'organisation_actions',
		'current_access_status',
	)
	list_filter = (
		'package',
		'banding',
	)
	list_display_links = (
		'pk',
		'institution',
	)
	raw_id_fields = (
		'package',
		'banding',
	)
	search_fields = (
		'institution',
		'first_name',
		'last_name',
		'email_address',
	)
	ordering = (
		'-pk',
		'institution',
	)

	def organisation_actions(self, obj):
		url = reverse('admin:%s_%s_add' % ('signup', 'accesslog'))
		if obj.admin_action_button() == 'grant':
			return format_html(
				'<a target="_blank" href="{url}?access_type={type}&signup={signup}" class="button">Grant Access</a>'.format(
					url=url,
					type='grant',
					signup=obj.pk,
				)
			)
		else:
			return format_html(
				'<a target="_blank" href="{url}?access_type={type}&signup={signup}" class="button">Revoke Access</a>'.format(
					url=url,
					type='revoke',
					signup=obj.pk,
				)
			)


class ContactAdmin(SummernoteModelAdmin):
	list_display = (
		'name',
		'email',
		'country',
		'contact_type',
	)
	list_filter = (
		'country',
		'contact_type',
	)
	raw_id_fields = (
		'country',
	)
	search_fields = (
		'name',
		'email',
		'contact_type',
	)


class OrganisationAdmin(SummernoteModelAdmin):
	list_display = (
		'name',
		'contact_email',
	)
	summernote_fields = (
		'hero_card_one_text',
		'hero_card_two_text',
		'hero_card_three_text',
		'about',
		'privacy',
		'billing_manager_message',
		'institution_message',
		'FAQ',
		'resources',
	)


class ResourceAdmin(SummernoteModelAdmin):
	list_display = (
		'title',
		'file',
		'order',
	)
	search_fields = (
		'title',
	)
	raw_id_fields = (
		'organisation',
	)


class NewsAdmin(SummernoteModelAdmin):
	list_display = (
		'title',
		'posted_by',
		'posted',
		'organisation',
	)
	search_fields = (
		'title',
	)
	list_filter = (
		'organisation',
		'posted_by',
	)
	raw_id_fields = (
		'organisation',
	)
	save_as = True


class AccessLogAdmin(admin.ModelAdmin):
	form = forms.AccessLogForm

	list_display = (
		'signup',
		'access_type',
		'user',
		'date_stamp',
	)

	def get_form(self, request, obj=None, **kwargs):
		AccessLogForm = super(AccessLogAdmin, self).get_form(request, obj, **kwargs)

		class RequestAccessForm(AccessLogForm):
			def __new__(cls, *args, **kwargs):
				kwargs['request'] = request
				return AccessLogForm(*args, **kwargs)

		return RequestAccessForm


class AccessLogExportCodeAdmin(admin.ModelAdmin):
	list_display = (
		'issued_to',
		'uuid',
		'active',
	)
	list_filter = (
		'active',
	)


admin_list = [
	(models.Package, PackageAdmin),
	(models.Country, CountryAdmin),
	(models.Banding, BandingAdmin),
	(models.SignUp, SignUpAdmin),
	(models.Contact, ContactAdmin),
	(models.Organisation, OrganisationAdmin),
	(models.Resource, ResourceAdmin),
	(models.NewsItem, NewsAdmin),
	(models.AccessLog, AccessLogAdmin),
	(models.AccessLogExportCode, AccessLogExportCodeAdmin),
]

[admin.site.register(*t) for t in admin_list]
