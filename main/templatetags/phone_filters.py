from django import template

register = template.Library()

@register.filter
def format_phone(value):
    if value and len(value) == 10 and value.isdigit():
        return f"({value[0:3]}) {value[3:6]}-{value[6:]}"
    return value
