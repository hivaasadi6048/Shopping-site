# cart/cart.py
from products.models import Product
from .models import CartItem
from django.db import models


class Cart:
    def __init__(self, request):
        """
        مدیریت سبد خرید کاربر.
        - اگر کاربر لاگین باشد، داده‌ها در دیتابیس ذخیره می‌شود.
        - اگر مهمان باشد، در session نگهداری می‌شود.
        """
        self.request = request
        self.session = request.session
        self.user = getattr(request, "user", None)
        self.cart = self.session.get("cart", {})
        self.session.setdefault("cart", self.cart)

    def add(self, product, quantity=1, replace_current_quantity=False):
        """
        افزودن محصول به سبد خرید.
        """
        if self.user and self.user.is_authenticated:
            # ذخیره در دیتابیس برای کاربر لاگین‌شده
            item, created = CartItem.objects.get_or_create(user=self.user, product=product)
            if replace_current_quantity:
                item.quantity = quantity
            else:
                item.quantity += quantity

            # اگر تعداد صفر یا منفی شد، حذفش کن
            if item.quantity <= 0:
                item.delete()
            else:
                item.save()
        else:
            # ذخیره در session برای کاربر مهمان
            product_id = str(product.id)
            if product_id not in self.cart:
                self.cart[product_id] = {
                    "quantity": 0,
                    "title": product.title,
                    "price": float(product.price),
                    "image_url": product.image.url if getattr(product, "image", None) else "",
                }

            if replace_current_quantity:
                self.cart[product_id]["quantity"] = quantity
            else:
                self.cart[product_id]["quantity"] += quantity

            # اگر تعداد صفر یا منفی شد، حذفش کن
            if self.cart[product_id]["quantity"] <= 0:
                del self.cart[product_id]

            self.save()

    def remove(self, product):
        """
        حذف محصول از سبد خرید.
        """
        if self.user and self.user.is_authenticated:
            CartItem.objects.filter(user=self.user, product=product).delete()
        else:
            product_id = str(product.id)
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()

    def save(self):
        """
        ذخیره تغییرات در session برای کاربران مهمان.
        """
        self.session["cart"] = self.cart
        self.session.modified = True

    def clear(self):
        """
        پاک کردن کل سبد خرید.
        """
        if self.user and self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
        self.session["cart"] = {}
        self.save()

    def __len__(self):
        """
        تعداد کل آیتم‌ها در سبد خرید.
        """
        if self.user and self.user.is_authenticated:
            total = CartItem.objects.filter(user=self.user).aggregate(total=models.Sum("quantity"))["total"] or 0
            return int(total)
        return sum(item["quantity"] for item in self.cart.values())

    def is_empty(self):
        return self.__len__() == 0

    def items(self):
        """
        برگرداندن آیتم‌های سبد خرید برای نمایش در قالب‌ها.
        """
        if self.user and self.user.is_authenticated:
            qs = CartItem.objects.filter(user=self.user).select_related("product")
            for item in qs:
                product = item.product
                price = float(product.price)
                yield {
                    "product_obj": product,
                    "quantity": item.quantity,
                    "price": price,
                    "title": getattr(product, "title", str(product)),
                    "image_url": product.image.url if getattr(product, "image", None) else "",
                    "total_price": price * item.quantity,
                }
        else:
            product_ids = [int(pid) for pid in self.cart.keys()]
            products = Product.objects.filter(id__in=product_ids)
            product_map = {p.id: p for p in products}

            for pid, item in list(self.cart.items()):
                prod_id = int(pid)
                product = product_map.get(prod_id)
                if product:
                    yield {
                        "product_obj": product,
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "title": item["title"],
                        "image_url": item["image_url"],
                        "total_price": item["price"] * item["quantity"],
                    }

    def get_total_price(self):
        """
        جمع کل قیمت سبد خرید.
        """
        total = 0
        for item in self.items():
            total += item["total_price"]
        return total
