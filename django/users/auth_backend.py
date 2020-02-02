from django.contrib.auth.backends import BaseBackend

from users.models import User


class PhpbbBackend(BaseBackend):
    def authenticate(self, request, *args, **kwargs):
        return None

    def get_user(self, user_id):
        return User.objects.get(user_id)
