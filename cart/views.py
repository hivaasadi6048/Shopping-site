from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from urllib.parse import urlparse
from .cart import Cart
from products.models import Product
from .forms import AddToCartProductForm
from django.contrib import messages


def safe_referer_redirect(request, default_name='cart:cart_detail'):
    """ریدایرکت فقط به آدرس‌های داخلی (جلوگیری از Open Redirect)"""
    referer = request.META.get("HTTP_REFERER")
    if referer:
        parsed = urlparse(referer)
        if not parsed.netloc or parsed.netloc == request.get_host():
            return redirect(referer)
    return redirect(default_name)


def cart_detail_view(request):
    cart = Cart(request)

    for item in cart.items():  # <-- استفاده از items() به جای iterable مستقیم
        item['product_update_quantity_form'] = AddToCartProductForm(initial={
            'quantity': item['quantity'],
            'inplace': True,
        })

    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def add_to_cart_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, active=True)
    form = AddToCartProductForm(request.POST)

    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        inplace = cleaned_data['inplace']

        # 🔒 بررسی موجودی و فعال بودن محصول
        if product.stock <= 0:
            messages.error(request, f'{product.title} موجود نیست.')
        elif quantity > product.stock:
            messages.error(request, f'تعداد درخواستی بیشتر از موجودی ({product.stock}) است.')
        else:
            cart.add(product, quantity, replace_current_quantity=True)
            messages.success(request, f'{product.title} با موفقیت به سبد خرید اضافه شد.')
    else:
        messages.error(request, 'اطلاعات فرم معتبر نیست.')

    # ✅ برگشت فقط به آدرس داخلی (جلوگیری از Open Redirect)
    return safe_referer_redirect(request)


@require_POST
def remove_from_cart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, f'{product.title} از سبد خرید حذف شد.')
    return safe_referer_redirect(request)


@require_POST
def clear_cart(request):
    cart = Cart(request)
    if not cart.is_empty():
        cart.clear()
        messages.success(request, 'تمام محصولات با موفقیت حذف شدند.')
    else:
        messages.warning(request, 'سبد خرید شما خالی است.')

    return safe_referer_redirect(request)
