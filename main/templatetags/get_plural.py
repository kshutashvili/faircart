from django import template
from pytils.numeral import get_plural


register = template.Library()
register.filter(name='get_plural', filter_func=get_plural)
