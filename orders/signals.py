from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .utils import generate_invoice_screenshot

@receiver(post_save, sender=Order)
def create_invoice_on_payment(sender, instance, created, **kwargs):
    # فقط وقتی سفارش پرداخت شده و هنوز فاکتور ندارد:
    # فاکتور + PDF + ایمیل (ذخیره‌های بعدی مثل تغییر وضعیت، ایمیل مجدد نمی‌فرستند)
    if instance.is_paid and not hasattr(instance, 'invoice'):
        instance.create_invoice()  # ایجاد رکورد فاکتور در دیتابیس
        try:
            generate_invoice_screenshot(instance)  # ایجاد فایل PDF و ارسال ایمیل
        except Exception as e:
            print("خطا در تولید PDF فاکتور:", e)