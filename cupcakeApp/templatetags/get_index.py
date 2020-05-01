from django import template
register = template.Library()

@register.filter(name='index')
def get_index(indexable, i):
    return indexable[i]
