# accounts/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from cart.models import CartItem
from products.models import Product


@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):
    """
    وقتی کاربر لاگین می‌کند، سبد خرید session را با سبد دیتابیس ادغام می‌کند.
    """
    session_cart = request.session.get('cart', {})

    if not session_cart:
        return  # سبد session خالی است، نیازی به ادغام نیست

    for product_id, item_data in session_cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            continue

        quantity = item_data.get("quantity", 1)
        if quantity <= 0:
            continue

        # بررسی آیا محصول از قبل در سبد دیتابیس وجود دارد؟
        cart_item, created = CartItem.objects.get_or_create(
            user=user,
            product=product,
            defaults={"quantity": quantity},  # مقدار اولیه اگر ایجاد شد
        )

        if not created:
            # اگر قبلاً وجود داشته، فقط تعداد را اضافه کن
            cart_item.quantity += quantity
            cart_item.save()

    # بعد از merge، سبد session را خالی کن
    request.session["cart"] = {}
    request.session.modified = True
