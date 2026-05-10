from django import template

register = template.Library()

@register.filter
def inr(value):
    """Format value with ₹ and two decimal points."""
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return value
