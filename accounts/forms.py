from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from allauth.account.forms import SignupForm

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'شماره موبایل یا رمز عبور اشتباه است.',
        'inactive': 'این حساب کاربری غیرفعال است.',
    }

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(self.error_messages['inactive'])


class CustomUserCreationForm(UserCreationForm):
    error_messages = {
        'password_mismatch': 'رمز عبورها همخوانی ندارند.',
        'password_too_short': 'رمز عبور باید حداقل ۸ کاراکتر باشد.',
        'password_too_common': 'رمز عبور بسیار رایج است.',
        'password_numeric_only': 'رمز عبور نمی‌تواند فقط از اعداد تشکیل شود.',
    }

    class Meta:
        model = User
        fields = (
            "phone_number",
            "password1",
            "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("phone_number", "email")


class CustomSignupForm(SignupForm):

    phone_number = forms.CharField(
        max_length=11,
        label="شماره موبایل"
    )
    email = forms.EmailField(
        required=False,
        label="ایمیل (اختیاری - برای دریافت فاکتور)"
    )

    def save(self, request):
        user = super().save(request)

        user.phone_number = self.cleaned_data["phone_number"]

        email = self.cleaned_data.get("email")
        if email:
            user.email = email

        user.username = self.cleaned_data["phone_number"]

        user.save()

        return user