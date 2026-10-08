from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .models import Product, Category, Order, OrderItem, Review
from .cart import Cart
from .forms import RegisterForm, CheckoutForm, ReviewForm


def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    query = request.GET.get('q')
    category_slug = request.GET.get('category')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'categories': categories,
        'query': query or '',
        'active_category': category_slug or '',
    }
    return render(request, 'store/home.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    reviews = product.reviews.select_related('user')
    user_has_reviewed = (
        request.user.is_authenticated and reviews.filter(user=request.user).exists()
    )
    review_form = ReviewForm()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
        'review_form': review_form,
    })


@login_required
@require_POST
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if Review.objects.filter(product=product, user=request.user).exists():
        messages.warning(request, "You've already reviewed this product.")
        return redirect('product_detail', slug=slug)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        messages.success(request, "Thanks for your feedback!")
    else:
        messages.error(request, "Please provide a valid rating and comment.")
    return redirect('product_detail', slug=slug)


@require_POST
def add_to_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f"{product.name} added to your cart.")
    return redirect(request.POST.get('next', 'home'))


@require_POST
def update_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity <= 0:
        cart.remove(product)
        messages.info(request, f"{product.name} removed from cart.")
    else:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, "Cart updated.")
    return redirect('cart_detail')


@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} removed from cart.")
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('home')

    initial = {}
    if request.user.is_authenticated:
        initial = {'full_name': request.user.get_full_name() or request.user.username,
                   'email': request.user.email}

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total_price = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
                product = item['product']
                if product.stock >= item['quantity']:
                    product.stock -= item['quantity']
                    product.save()

            cart.clear()
            return redirect('order_success', order_id=order.id)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {'order': order})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


class StoreLoginView(LoginView):
    template_name = 'registration/login.html'


def store_logout(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/my_orders.html', {'orders': orders})


@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if not order.can_cancel:
        messages.error(request, "This order can no longer be cancelled.")
        return redirect('my_orders')

    # restore stock for each item
    for item in order.items.all():
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    order.status = 'cancelled'
    order.save()
    messages.success(request, f"Order #{order.id} has been cancelled.")
    return redirect('my_orders')


@require_POST
def set_currency(request):
    code = request.POST.get('currency', 'INR')
    if code in ('INR', 'USD', 'EUR', 'GBP'):
        request.session['currency'] = code
    next_url = request.POST.get('next') or 'home'
    return redirect(next_url)
