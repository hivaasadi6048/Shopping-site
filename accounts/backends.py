from django.contrib.auth import get_user_model

User = get_user_model()


def get_client_username(request, credentials=None):
    """
    استخراج نام کاربری برای django-axes.
    هم فرم ورود allauth (فیلد login) و هم فرم ورود ادمین (فیلد username)
    پشتیبانی می‌شود تا قفل بر اساس نام‌کاربری درست کار کند.
    """
    if credentials:
        return credentials.get('login') or credentials.get('username')
    data = getattr(request, 'data', None) or request.POST
    return data.get('login') or data.get('username')


class PhoneBackend:

    def authenticate(self, request, username=None, password=None, **kwargs):

        login = kwargs.get("login", username)

        try:
            user = User.objects.get(phone_number=login)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None