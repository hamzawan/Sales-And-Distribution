from django import template
from transaction.models import ChartOfAccount

register = template.Library()

@register.simple_tag
def child_account_custom_tag(id):
    childs = ChartOfAccount.objects.filter(parent_id = id).all()
    return {'childs' : childs}