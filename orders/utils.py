from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import os
import arabic_reshaper
from bidi.algorithm import get_display

import barcode
from barcode.writer import ImageWriter
from PIL import Image


def generate_invoice_screenshot(order):
    """
    - تولید PDF فاکتور فارسی (RTL)
    - افزودن بارکد سفارش
    - ذخیره در media/invoices
    - ارسال خودکار ایمیل به کاربر با PDF پیوست
    """

    # ================= مسیرها =================
    invoice_dir = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(invoice_dir, exist_ok=True)

    pdf_path = os.path.join(invoice_dir, f'invoice_{order.id}.pdf')
    barcode_path = os.path.join(invoice_dir, f'barcode_{order.id}.png')

    
    # ================= فونت فارسی =================
    font_path = os.path.join(
        settings.BASE_DIR, 'static', 'fonts', 'Vazirmatn-Regular.ttf'
    )

    if "Vazirmatn" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("Vazirmatn", font_path))

    # ================= ساخت بارکد =================
    Code128 = barcode.get_barcode_class('code128')
    code = Code128(str(order.id), writer=ImageWriter())
    code.save(barcode_path.replace('.png', ''))

    # ================= ایجاد PDF =================
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    def draw_rtl(text, x, y, size=12):
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        c.setFont("Vazirmatn", size)
        c.drawRightString(x, y, bidi_text)

    y = height - 40

    # هدر
    draw_rtl("🛍️ فروشگاه exeexe", width - 50, y, 16)
    y -= 25
    draw_rtl(f"🧾 فاکتور سفارش #{order.id}", width - 50, y, 14)

    c.line(40, y - 10, width - 40, y - 10)
    y -= 40

    # اطلاعات مشتری
    draw_rtl(f"👤 مشتری: {order.first_name} {order.last_name}", width - 50, y)
    y -= 20
    draw_rtl(f"📞 تلفن: {order.phone_number}", width - 50, y)
    y -= 20
    draw_rtl(f"📍 آدرس: {order.address}", width - 50, y)
    y -= 40

    # بارکد
    barcode_img = Image.open(barcode_path)
    bw, bh = barcode_img.size
    scale = 0.45
    c.drawInlineImage(
        barcode_path,
        50,
        y - (bh * scale),
        bw * scale,
        bh * scale
    )
    y -= (bh * scale) + 20

    # جدول محصولات
    draw_rtl("نام محصول", width - 350, y)
    draw_rtl("تعداد", width - 180, y)
    draw_rtl("قیمت", width - 70, y)
    y -= 15
    c.line(40, y, width - 40, y)
    y -= 25

    for item in order.items.all():
        draw_rtl(item.product.title[:40], width - 350, y)
        draw_rtl(item.quantity, width - 180, y)
        draw_rtl(f"{item.price:,}", width - 70, y)
        y -= 20

        if y < 100:
            c.showPage()
            y = height - 50

    c.line(40, y, width - 40, y)
    y -= 30
    draw_rtl(
        f"💰 مبلغ کل: {order.get_total_price():,} تومان",
        width - 50,
        y,
        13
    )

    c.save()

    # ================= ارسال ایمیل (فقط اگر کاربر ایمیل داشته باشد) =================
    user_email = getattr(order.user, "email", "")
    if user_email:
        subject = f"فاکتور سفارش #{order.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user_email]

        html_content = render_to_string(
            "orders/invoice_email.html",
            {"order": order}
        )

        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.attach_file(pdf_path)
        msg.send()

    return pdf_path
