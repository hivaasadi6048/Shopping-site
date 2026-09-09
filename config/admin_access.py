# core/admin_access.py
from django.contrib import admin
from django.shortcuts import redirect

def custom_admin_permission(request):
    """
    فقط سوپریوزر اجازه ورود به پنل ادمین اصلی را دارد.
    سایر کاربران (staff یا user معمولی) به پنل سفارشی منتقل می‌شوند.
    """
    if request.user.is_active and request.user.is_superuser:
        # اجازه ورود به پنل اصلی
        return True

    elif request.user.is_authenticated:
        # اگر لاگین کرده ولی سوپریوزر نیست → ریدایرکت به پنل سفارشی
        return redirect('adminpanel:home')

    else:
        # اگر لاگین نکرده → هدایت به صفحه‌ی لاگین
        return redirect('account/login')

# حالا تابع رو به admin site وصل می‌کنیم:
admin.site.has_permission = custom_admin_permission
