from .cart import Cart
from .currency import SYMBOLS


def cart_summary(request):
    cart = Cart(request)
    return {'cart_item_count': len(cart)}


def currency_context(request):
    code = request.session.get('currency', 'INR')
    return {
        'current_currency': code,
        'current_currency_symbol': SYMBOLS.get(code, '₹'),
    }
