from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils import generate_invoice_screenshot

@receiver(post_save, sender=Order)
def create_invoice_on_payment(sender, instance, created, **kwargs):
    # اگر سفارش پرداخت شده و فاکتور ندارد، آن را ایجاد کن
    if instance.is_paid and not hasattr(instance, 'invoice'):
        invoice = instance.create_invoice()  # ایجاد رکورد فاکتور در دیتابیس
    try:
        generate_invoice_screenshot(instance)  # ایجاد فایل PDF
    except Exception as e:
            print("خطا در تولید PDF فاکتور:", e)