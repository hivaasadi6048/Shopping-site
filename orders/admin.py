from django.contrib import admin
from . models import Order, OrderItem, Invoice, InvoiceItem
from jalali_date.admin import ModelAdminJalaliMixin


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['order', 'product' , 'quantity','price',]
    extra = 1


@admin.register(Order)
class OrderAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display = ['user', 'first_name','last_name', 'datetime_created','is_paid',]

    inlines=[
        OrderItemInline,
    ]



@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product' , 'quantity','price', ]




class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    readonly_fields = ('product_name', 'quantity', 'unit_price', 'line_total')
    can_delete = False
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'issued_at', 'total', 'status')
    inlines = [InvoiceItemInline]
    readonly_fields = ('invoice_number', 'created_at')
