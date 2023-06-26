from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """User model."""

    USER = 'user'
    ADMIN = 'admin'

    USER_ROLES_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    username = models.CharField(
        'username',
        unique=True,
        max_length=150,
        blank=False,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+'
            )
        ]
    )
    email = models.EmailField(
        'email address',
        unique=True,
        max_length=254,
        blank=False,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
        blank=False,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
        blank=False,
    )
    role = models.CharField(
        choices=USER_ROLES_CHOICES,
        default='user',
        max_length=13,
        blank=True,
    )
    is_subscribed = models.BooleanField(
        'is_subscribed',
        max_length=5,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_name'
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == User.ADMIN

    @property
    def is_admin_or_superuser(self):
        return self.role == User.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == User.USER


class Follow(models.Model):
    """Follow model."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        ordering = ('-id',)
        db_table = 'users_follows'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following', ],
                name='unique_follow'
            )
        ]
