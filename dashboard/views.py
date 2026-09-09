from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, logout
from .forms import ProfileForm, CustomPasswordChangeForm, AddressForm
from orders.models import Address 

# داشبورد اصلی
@login_required
def dashboard(request):

    address = Address.objects.filter(
        user=request.user
    ).first()

    context = {
        "address": address
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context
    )

# logout امن
@login_required
def logout_view(request):
    logout(request)
    return redirect('products:product_list')

# پروفایل
@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()        
            messages.success(request, "پروفایل با موفقیت به‌روزرسانی شد ✅")
            return redirect('dashboard:profile')
        else:
            messages.error(request, "لطفاً خطاهای فرم را اصلاح کنید ❌")
    else:
        form = ProfileForm(instance=user)
    return render(request, "dashboard/profile.html", {"form": form})

# تغییر رمز
@login_required
def change_password_view(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # برای جلوگیری از logout بعد تغییر رمز
            messages.success(request, "رمز عبور با موفقیت تغییر کرد ✅")
            return redirect('dashboard:change_password')
        else:
            messages.error(request, "لطفاً خطاهای فرم را اصلاح کنید ❌")
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, "dashboard/change_password.html", {"form": form})

# مدیریت آدرس‌ها
@login_required
def address_list_view(request):
    addresses = Address.objects.filter(user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "آدرس با موفقیت اضافه شد ✅")
            return redirect('dashboard:address_list')
        else:
            messages.error(request, "لطفاً خطاهای فرم را اصلاح کنید ❌")
    else:
        form = AddressForm()
    return render(request, "dashboard/address_list.html", {"addresses": addresses, "form": form})


@login_required
def wishlist_view(request):
    # فرض: wishlisted_products می‌تواند از مدل Wishlist یا Product گرفته شود
    # برای نمونه، الان فقط صفحه ساده نمایش داده می‌شود
    return render(request, "dashboard/wishlist.html")



#--------------------------حذف آدرس #
@login_required
def delete_address_view(request, pk):

    address = Address.objects.get(
        id=pk,
        user=request.user
    )

    address.delete()

    messages.success(
        request,
        "آدرس حذف شد"
    )

    return redirect(
        'dashboard:address_list'
    )