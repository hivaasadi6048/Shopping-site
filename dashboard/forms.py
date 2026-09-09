from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from orders.models import Address  # فرض می‌کنیم مدل Address در اپ orders است

User = get_user_model()

# فرم تغییر پروفایل
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','phone_number',]

# فرم تغییر رمز عبور
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز فعلی'}),
        label='رمز فعلی'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز جدید'}),
        label='رمز جدید'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز جدید'}),
        label='تکرار رمز جدید'
    )

# فرم مدیریت آدرس
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['title', 'address_line', 'city', 'postal_code', 'phone_number']

