from django.shortcuts import get_object_or_404, reverse
from django.http import Http404
from django.http.request import split_domain_port

from signup import models


class BaseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


class OrganisationMiddleware(BaseMiddleware):
    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith(reverse('admin:index')) or request.path.startswith('/summernote'):
            return None

        domain = request.get_host()
        try:
            organisation = models.Organisation.objects.get(
                domain=domain,
            )
        except models.Organisation.DoesNotExist:
            domain, _port = split_domain_port(domain)
            organisation = get_object_or_404(
                models.Organisation,
                domain=domain,
            )

        if not organisation:
            raise Http404

        request.organisation = organisation




