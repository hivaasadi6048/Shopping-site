from decimal import Decimal
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('در انتظار')),
        ('processing', _('در حال پردازش')),
        ('paid', _('پرداخت‌شده')),
        ('shipped', _('ارسال‌شده')),
        ('cancelled', _('لغو‌شده')),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('کاربر')
    )
    first_name = models.CharField(max_length=100, verbose_name=_('نام'))
    last_name = models.CharField(max_length=100, verbose_name=_('نام خانوادگی'))
    phone_number = models.CharField(max_length=15, verbose_name=_('شماره تلفن'))
    address = models.CharField(max_length=700, verbose_name=_('آدرس'))
    order_notes = models.CharField(max_length=700, blank=True, verbose_name=_('یادداشت سفارش'))
    is_paid = models.BooleanField(default=False, verbose_name=_('پرداخت شده'))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('وضعیت سفارش')
    )
    zarinpal_authority = models.CharField(max_length=255, blank=True, verbose_name=_('شماره مجوز زرین‌پال'))
    zarinpal_ref_id = models.CharField(max_length=150, blank=True, verbose_name=_('شناسه مرجع زرین‌پال'))
    zarinpal_data = models.TextField(blank=True, verbose_name=_('داده‌های زرین‌پال'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ تغییر'))

    class Meta:
        verbose_name = _('سفارش')
        verbose_name_plural = _('سفارش‌ها')
        ordering = ['-datetime_created']

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    def get_total_price(self):
        total = Decimal('0.00')
        for item in self.items.all():
            total += (Decimal(item.price) * item.quantity)
        return total

    def create_invoice(self):
        """
        Create an invoice from this order — if it exists, return the existing one.
        This method snapshots order items in InvoiceItem.
        """
        from django.apps import apps

        Invoice = apps.get_model('orders', 'Invoice')
        InvoiceItem = apps.get_model('orders', 'InvoiceItem')

        if hasattr(self, 'invoice'):
            return self.invoice

        invoice = Invoice.objects.create(
            order=self,
            total=self.get_total_price(),
            issued_at=timezone.now()
        )

        for item in self.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                product=item.product,
                product_name=str(item.product),
                quantity=item.quantity,
                unit_price=Decimal(item.price),
                line_total=(Decimal(item.price) * item.quantity)
            )

        return invoice





class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="addresses")
    title = models.CharField(max_length=100)  # مثلا خانه، محل کار
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'OrderItem {self.id}:{self.product} * {self.quantity} (price:{self.price})'


# ---------- Invoice related models ----------
class Invoice(models.Model):
    STATUS_CHOICES = (
        ('issued', 'Issued'),
        ('cancelled', 'Cancelled'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=64, unique=True, editable=False)
    issued_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ('-issued_at',)

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # قالب شماره فاکتور: INV-YYYYMMDD-<8hex>
            self.invoice_number = f"INV-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        if self.total is None:
            # در صورتی که مقدار total پاس داده نشده باشد، از سفارش محاسبه می‌کنیم
            self.total = self.order.get_total_price()
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey("products.Product", on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=300)  # snapshot اسم محصول
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=0)

    def save(self, *args, **kwargs):
        # تضمین محاسبه مقدار خط
        self.line_total = (Decimal(self.unit_price) * self.quantity)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} x {self.quantity} ({self.line_total})"
