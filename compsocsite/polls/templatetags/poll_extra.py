from django import template
import numpy as np
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def largest(l):
    return max(l)
    
@register.filter
def smallest(l):
    return min(l)
    
@register.filter
def index(sequence, position):
    return sequence[position]

@register.filter
@stringfilter
def random_utility(original_value):
	try:
		sigma = 10
		base = float(original_value)
		utility = round(np.random.normal(0.0,sigma)+ base)
		return str(utility)
	except:
		return original_value