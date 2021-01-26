"""Byers A, Sanchez, M & Eve Janeway https://github.com/BirkbeckCTP/janeway/blob/master/src/core/templatetags/truncate.py"""

from django import template
from django.utils.html import mark_safe

register = template.Library()


@register.filter
def truncatesmart(value, limit=80):
    """
    Truncates strings keeping whole words. Usage:
    {% load truncate %}
    {{ string|truncatesmart }}
    {{ string|truncatesmart:100 }}
    """
    if not value:
        return ''

    try:
        limit = int(limit)
    except ValueError:
        return mark_safe(value)

    if len(value) <= limit:
        return mark_safe(value)

    value = value[:limit]
    words = value.split(' ')[:-1]

    return mark_safe(' '.join(words) + ' [...]')