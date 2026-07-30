from django import template

register = template.Library()

@register.filter
def role_color(role):
    colors = {
        "suspect": "#ffe6e6",   # светло-красный
        "witness": "#e6f3ff",  # светло-голубой
        "victim": "#fff3e6",   # светло-оранжевый
        "other": "#f3f3f3",    # светло-серый
    }
    return colors.get(role, "#f3f3f3")