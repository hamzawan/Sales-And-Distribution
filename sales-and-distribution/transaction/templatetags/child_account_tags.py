from django import template
from transaction.models import ChartOfAccount
from django.http import JsonResponse, HttpResponse

register = template.Library()

@register.simple_tag
def child_account_custom_tag(id):
    child_list = []
    childs = ChartOfAccount.objects.filter(parent_id = id).all()
    for i in childs:
        print("     ",i.account_title)
    for value in childs:
        info = {
                "id": value.id,
                "account_title" : value.account_title
            }
        child_list.append(info)
    return {'childs' : child_list}