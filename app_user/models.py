from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=10, unique=True, db_index=True)
    gender = models.CharField(
        max_length=6,
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
    )
    country = models.CharField(max_length=50)
    interests = models.ManyToManyField("Interest", db_index=True)
    is_online = models.BooleanField(default=False, db_index=True)
    current_connection = models.OneToOneField(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        related_name="connected_user",
        default=None,
        db_index=True,
    )

    def __str__(self):
        return self.username


class Interest(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name
