from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='first name'
    )
    last_name = models.CharField(
        blank=False,
        max_length=150,
        verbose_name='last name'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'Пользователь'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='subscribed',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'{self.user} is subcribed to {self.author}'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='no_self_subscribe'
            ),

            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribing'
            )
        ]
