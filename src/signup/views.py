import csv

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.html import strip_tags

from signup import models, forms


def index(request):
	packages = models.Package.objects.filter(
		organisation=request.organisation,
		hidden=False,
	)
	front_page_packages =packages.filter(
		organisation=request.organisation,
		front_page=True,
	)
	template = 'signup/index.html'
	context = {
		'packages': packages,
		'front_page_packages': front_page_packages,
	}
	return render(
		request,
		template,
		context,
	)


def packages(request):
	packages = models.Package.objects.filter(
		organisation=request.organisation,
		hidden=False,
	)
	template = 'signup/packages.html'
	context = {
		'packages': packages,
	}
	return render(
		request,
		template,
		context,
	)


def package(request, package_id):
	package = get_object_or_404(
		models.Package,
		pk=package_id,
		hidden=False,
	)
	template = 'signup/package.html'
	context = {
		'package': package,
	}
	return render(
		request,
		template,
		context,
	)


def page(request, page_name):
	if page_name == 'privacy':
		content = request.organisation.privacy
	elif page_name == 'about':
		content = request.organisation.about
	elif page_name == 'FAQ':
		content = request.organisation.FAQ
	else:
		content = None

	template = 'signup/page.html'
	context = {
		'content': content,
		'page_name': page_name,
	}
	return render(
		request,
		template,
		context,
	)


def signup_start(request, package_id):
	form = forms.SignupStart()
	package = get_object_or_404(
		models.Package,
		hidden=False,
		pk=package_id,
	)

	if request.POST:
		form = forms.SignupStart(request.POST)
		if form.is_valid():
			return redirect(
				reverse(
					'signup_banding',
					kwargs={
						'package_id': package.pk,
						'country_code': form.data['country'],
					}
				)
			)

	template = 'signup/start.html'
	context = {
		'form': form,
		'package': package,
	}
	return render(
		request,
		template,
		context,
	)


def signup_banding(request, package_id, country_code):
	package = get_object_or_404(
		models.Package,
		hidden=False,
		pk=package_id,
	)
	country = get_object_or_404(
		models.Country,
		code=country_code,
	)
	bandings = models.Banding.objects.filter(
		country=country,
	)

	# If no bandings are found we want to display those without Countries
	# which are the defaults.
	if not bandings.exists():
		bandings = models.Banding.objects.filter(
			country__isnull=True,
		)

	form = forms.BandingForm(
		bandings=bandings,
	)
	if request.POST:
		form = forms.BandingForm(
			request.POST,
			bandings=bandings,
		)

		if form.is_valid():
			return redirect(
				reverse(
					'signup_data',
					kwargs={
						'package_id': package.pk,
						'country_code': country.code,
						'banding_id': form.data['banding'],
					}
				)
			)

	template = 'signup/bandings.html'
	context = {
		'package': package,
		'country': country,
		'bandings': bandings,
		'form': form,
	}
	return render(
		request,
		template,
		context,
	)


def signup_data(request, package_id, country_code, banding_id):
	package = get_object_or_404(
		models.Package,
		hidden=False,
		pk=package_id,
	)
	country = get_object_or_404(
		models.Country,
		code=country_code,
	)
	banding = get_object_or_404(
		models.Banding,
		pk=banding_id,
	)
	if banding.country and banding.country != country:
		raise Http404

	form = forms.SignUpForm()

	if request.POST:
		form = forms.SignUpForm(
			request.POST,
		)
		if form.is_valid():
			signup = form.save(commit=False)
			signup.process_complete(
				request.organisation,
				banding,
				package,
			)
			return redirect(
				'signup_thanks',
			)

	template = 'signup/signup.html'
	context = {
		'package': package,
		'country': country,
		'banding': banding,
		'form': form,
	}
	return render(
		request,
		template,
		context,
	)


def signup_thanks(request):
	template = 'signup/thanks.html'
	context = {}
	return render(
		request,
		template,
		context,
	)


def resources(request):
	template = 'signup/resources.html'
	context = {
		'organisation': request.organisation,
	}
	return render(
		request,
		template,
		context,
	)


def news(request):
	news_items = models.NewsItem.objects.filter(
		organisation=request.organisation,
	)
	paginator = Paginator(news_items, 10)
	page = request.GET.get('page', 1)

	try:
		news_items = paginator.page(page)
	except PageNotAnInteger:
		news_items = paginator.page(1)
	except EmptyPage:
		news_items = paginator.page(paginator.num_pages)
	template = 'signup/news.html'
	context = {
		'organisation': request.organisation,
		'news_items': news_items,
		'page': page,
	}
	return render(
		request,
		template,
		context,
	)


def news_item(request, news_id):
	news_item = get_object_or_404(
		models.NewsItem,
		pk=news_id,
		organisation=request.organisation
	)
	template = 'signup/news_item.html'
	context = {
		'news_item': news_item,
	}
	return render(
		request,
		template,
		context,
	)


def export_access_log(request, uuid):
	access_code = get_object_or_404(
		models.AccessLogExportCode,
		uuid=uuid,
		active=True,
	)
	log_entries = models.AccessLog.objects.filter(
		signup__package__organisation=access_code.organisation,
	)

	all_rows = []
	headers = [
		'Institution',
		'Address',
		'Tech Contact',
		'Package',
		'Date',
		'Grant or Revoke',
		'Email Address',
		'Phone Number',
		'IP Range',
		'Existing Customer?',
		'Payment Handler',
	]
	all_rows.append(headers)

	for entry in log_entries:
		row = [
			entry.signup.institution,
			entry.signup.address,
			entry.signup.technical_contact,
			entry.signup.package.name,
			entry.date_stamp,
			entry.access_type,
			entry.signup.email_address,
			entry.signup.phone_number,
			entry.ip_range,
			entry.signup.existing_customer,
			entry.payment_handler
		]
		all_rows.append(row)

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="access_log_export.csv"'
	writer = csv.writer(response)
	writer.writerows(all_rows)

	return response
