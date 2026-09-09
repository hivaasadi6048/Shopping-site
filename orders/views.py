from django.shortcuts import render,redirect, get_object_or_404
from .forms import OrderForm
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from .models import OrderItem
from django.contrib import messages
from .models import Invoice
from django.http import FileResponse, Http404
from django.conf import settings
import os


# اجبار به لاگین بودن کاربر برای ثبت سفارش
@login_required
def order_create_view(request):
    order_form = OrderForm
    cart = Cart(request)

# اخطار و ریدارکت کردن کاربر در صورت خالی بودن سبد خرید
    if len(cart)== 0:
        messages.warning(request, 'your cart is empty!')
        return redirect('products:product_list')
    
# ارسال سبد خرید و مشخصات سفارش به دیتابیس و پاک کردن سبد خرید
    if request.method == 'POST':
        order_form = OrderForm(request.POST,)

        if order_form.is_valid():
            order_obj = order_form.save(commit=False)
            order_obj.user = request.user
            order_obj.save()

            for item in cart.items():
                product = item['product_obj']
                OrderItem.objects.create(
                    order=order_obj,
                    product= product,
                    quantity= item['quantity'],
                    price = product.price,
                )
                # این الان هم session و هم دیتابیس رو پاک می‌کنه
            cart.clear()
            
# ذخیره نام و نام خانوادگی کاربر بعد از ثبت سفارش برای سفارش بعدی
            request.user.first_name = order_obj.first_name
            request.user.last_name = order_obj.last_name
            request.user.save()

            messages.success(request, 'yor order has successfuly placed.')

            request.session['order_id'] = order_obj.id
            return redirect('payment:payment_process')
       
    return render (request , 'orders/order_create.html', {
        'form':order_form
    })






@login_required
def invoice_detail(request, invoice_id):
    """نمایش یک فاکتور خاص"""
    invoice = get_object_or_404(Invoice, id=invoice_id, order__user=request.user)
    return render(request, "orders/invoice_detail.html", {"invoice": invoice})


@login_required
def my_invoices(request):
    """لیست همه فاکتورهای کاربر"""
    invoices = Invoice.objects.filter(order__user=request.user).order_by("-issued_at")
    return render(request, "orders/my_invoices.html", {"invoices": invoices})






def download_invoice_pdf(request, order_id):
    from .models import Order
    order = Order.objects.filter(id=order_id).first()
    if not order:
        raise Http404("سفارش پیدا نشد.")
    
    if request.user != order.user and not request.user.is_superuser:
        raise Http404("شما اجازه دسترسی به این فاکتور را ندارید.")

    # مسیر فایل PDF فاکتور
    invoice_file = os.path.join(settings.MEDIA_ROOT, f'invoices/invoice_{order.id}.pdf')
    if not os.path.exists(invoice_file):
        raise Http404("فایل فاکتور وجود ندارد.")
    
    return FileResponse(open(invoice_file, 'rb'), as_attachment=True, filename=f"invoice_{order.id}.pdf")
