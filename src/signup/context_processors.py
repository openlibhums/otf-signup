from django.conf import settings

from signup import models


def organisation(request):
	"""
	Adds an Organisation object to the Context.
	:param request: the active request
	:return: dictionary containing a Organisation object under key 'organisation' or None if this is a press site
	"""
	if hasattr(request, 'organisation'):
		return {'organisation': request.organisation}
	else:
		return {'organisation': None}


def site_domain(request):
	"""
	Injects the site domain into Django templates. This is hacky but fine for us.
	:param request: the active request
	:return: dict with key 'site_domain'.
	"""
	return settings.PRIMARY_BASE_DOMAIN