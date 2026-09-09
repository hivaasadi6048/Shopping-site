from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


#اجازه دسترسی به کاربران
def staff_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=settings.LOGIN_URL
    )(view_func)
#اجازه دسترسی فقط برای سوپریوزر
def superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_superuser,
        login_url=settings.LOGIN_URL
    )(view_func)
#اجازه دسترسی به هر دو 
def staff_or_superuser_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and (u.is_staff or u.is_superuser),
        login_url=settings.LOGIN_URL
    )(view_func)
