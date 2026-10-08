"""
Server-side currency conversion.
No JavaScript involved: the person clicks a plain <a> link to switch
currency, which sets a session value and redirects back. Every price
shown afterwards is converted on the server before the template ever
sees it.
"""

import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache

SYMBOLS = {'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£'}


def get_rate(target_currency):
    """Return the INR -> target_currency exchange rate, cached for 6 hours."""
    if target_currency == 'INR':
        return Decimal('1')

    rates = cache.get('exchange_rates')
    if rates is None:
        try:
            resp = requests.get(settings.EXCHANGE_RATE_API_URL, timeout=5)
            resp.raise_for_status()
            rates = resp.json().get('rates', {})
            cache.set('exchange_rates', rates, timeout=60 * 60 * 6)
        except requests.RequestException:
            return None
    return rates.get(target_currency)


def convert_amount(amount, target_currency):
    """Convert an INR amount to target_currency. Falls back to INR if the API fails."""
    if target_currency == 'INR':
        return amount, 'INR'
    rate = get_rate(target_currency)
    if rate is None:
        return amount, 'INR'
    return round(Decimal(str(amount)) * Decimal(str(rate)), 2), target_currency
