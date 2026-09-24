import json
import requests
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.urls import reverse
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django_ratelimit.decorators import ratelimit
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.utils import timezone
from orders.models import Order

# ----------------------------
# 🔹 توابع کمکی و ویوهای پرداخت زرین‌پال
# ----------------------------

def _env_urls_and_merchant():
    use_sandbox = getattr(
        settings,
        "ZARINPAL_USE_SANDBOX",
        True
    )

    if use_sandbox:
        return {
            "merchant_id": settings.ZARINPAL_SANDBOX_MERCHANT_ID,
            "request_url": "https://sandbox.zarinpal.com/pg/v4/payment/request.json",
            "startpay": "https://sandbox.zarinpal.com/pg/StartPay/",
            "verify": "https://sandbox.zarinpal.com/pg/v4/payment/verify.json",
        }

    return {
        "merchant_id": settings.ZARINPAL_MERCHANT_ID,
        "request_url": "https://payment.zarinpal.com/pg/v4/payment/request.json",
        "startpay": "https://payment.zarinpal.com/pg/StartPay/",
        "verify": "https://payment.zarinpal.com/pg/v4/payment/verify.json",
    }

@login_required
@ratelimit(key='user', rate='20/h', block=False)
def payment_process(request):
    """ارسال درخواست پرداخت به زرین‌پال"""
    if getattr(request, 'limited', False):
        messages.error(request, "تعداد درخواست پرداخت زیاد است. لطفاً چند دقیقه بعد تلاش کنید.")
        return redirect('cart:cart_detail')

    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "سفارشی برای پرداخت پیدا نشد. لطفاً دوباره سفارش ثبت کنید.")
        return redirect('cart:cart_detail')

    order = get_object_or_404(Order, id=order_id, user=request.user)
    rial_total_price = int(order.get_total_price() * 10)

    cfg = _env_urls_and_merchant()
    merchant_id = cfg["merchant_id"]
    zarinpal_request_url = cfg["request_url"]
    startpay_url = cfg["startpay"]

    # جلوگیری از ارسال درخواست تکراری
    if order.zarinpal_authority and not order.is_paid:
        return redirect(f"{startpay_url}{order.zarinpal_authority}")

    request_data = {
        "merchant_id": merchant_id,
        "amount": rial_total_price,
        "description": f'#{order.id}: {order.user.get_full_name()}',
        "callback_url": request.build_absolute_uri(reverse('payment:payment_callback')),
    }

    res = requests.post(
        url=zarinpal_request_url,
        data=json.dumps(request_data, cls=DjangoJSONEncoder),
        headers={"accept": "application/json", "content-type": "application/json"},
        timeout=20,
    )
    data = res.json()

    if "data" in data and data["data"].get("code") == 100:
        order.zarinpal_authority = data["data"]["authority"]
        order.save()
        return redirect(f"{startpay_url}{order.zarinpal_authority}")

    error = data.get("errors", {})
    messages.error(
        request,
        f"خطا در اتصال به درگاه پرداخت (کد {error.get('code')}). لطفاً دوباره تلاش کنید."
    )
    return render(request, "payment/payment_error.html", {"order": order}, status=400)






def payment_callback(request):
    """دریافت پاسخ از زرین‌پال پس از پرداخت"""

    authority = request.GET.get("Authority")
    status = request.GET.get("Status")

    if not authority or not status:
        messages.error(request, "پارامترهای پرداخت نامعتبر است.")
        return render(request, "payment/payment_error.html", status=400)

    order = get_object_or_404(
        Order,
        zarinpal_authority=authority
    )

    # جلوگیری از ثبت مجدد پرداخت
    if order.is_paid:
        messages.info(request, "این تراکنش قبلاً ثبت شده است")
        return redirect(
            'orders:invoice_detail',
            invoice_id=order.invoice.id
        )

    # کاربر پرداخت را لغو کرده
    if status != "OK":
        messages.warning(request, "پرداخت لغو شد. سفارش شما همچنان ثبت است.")
        return redirect('pages:home')

    cfg = _env_urls_and_merchant()

    verify_data = {
        "merchant_id": cfg["merchant_id"],
        "amount": int(order.get_total_price() * 10),
        "authority": authority,
    }

    try:
        res = requests.post(
            url=cfg["verify"],
            data=json.dumps(
                verify_data,
                cls=DjangoJSONEncoder
            ),
            headers={
                "accept": "application/json",
                "content-type": "application/json",
            },
            timeout=20,
        )

        res.raise_for_status()

    except requests.RequestException:
        messages.error(request, "خطا در ارتباط با درگاه پرداخت. لطفاً دوباره تلاش کنید.")
        return render(request, "payment/payment_error.html", {"order": order}, status=500)

    data = res.json().get("data", {})

    # پرداخت موفق
    if data.get("code") == 100:

        with transaction.atomic():

            order.is_paid = True
            order.ref_id = data.get("ref_id")
            order.zarinpal_data = json.dumps(
                data,
                cls=DjangoJSONEncoder
            )
            order.save()

            # کاهش موجودی محصولات + ثبت آمار فروش
            for item in order.items.select_related("product"):

                product = item.product

                product.stock -= item.quantity

                product.sales_count = (product.sales_count or 0) + item.quantity

                if product.stock <= 0:
                    product.stock = 0
                    product.active = False

                product.save()

        messages.success(
            request,
            f"پرداخت با موفقیت انجام شد ✅ کد رهگیری: {order.ref_id}"
        )

        return redirect(
            'orders:invoice_detail',
            invoice_id=order.invoice.id
        )

    # قبلاً تأیید شده
    elif data.get("code") == 101:

        messages.info(
            request,
            "این تراکنش قبلاً ثبت شده است"
        )

        return redirect(
            'orders:invoice_detail',
            invoice_id=order.invoice.id
        )

    messages.error(
        request,
        f"تراکنش ناموفق بود (کد {data.get('code')}). لطفاً دوباره تلاش کنید."
    )
    return render(request, "payment/payment_error.html", {"order": order}, status=400)