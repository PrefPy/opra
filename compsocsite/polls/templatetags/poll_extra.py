from django import template

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