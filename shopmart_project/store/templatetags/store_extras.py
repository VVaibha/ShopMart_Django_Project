from django import template
from store.currency import convert_amount, SYMBOLS

register = template.Library()


@register.simple_tag(takes_context=True)
def price(context, amount):
    """
    Usage in template: {% price product.price %}
    Converts `amount` (assumed to be in INR) to whatever currency is
    stored in the visitor's session, and renders it with the right
    symbol — e.g. "$29.99" or "₹2,499.00".
    """
    request = context['request']
    code = request.session.get('currency', 'INR')
    converted, resolved_code = convert_amount(amount, code)
    symbol = SYMBOLS.get(resolved_code, '₹')
    return f"{symbol}{converted}"
