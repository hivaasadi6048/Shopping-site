from django.contrib.auth import get_user_model

User = get_user_model()


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