from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('RIDER', 'Rider'),
        ('CUSTOMER', 'Customer'),
        ('STAFF', 'Staff'),
    ]

    first_name = models.CharField(_('first name'), max_length=150)
    middle_name = models.CharField(_('middle name'), max_length=150, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=150)
    user_role = models.CharField(_('user role'), max_length=10, choices=ROLE_CHOICES, default='CUSTOMER')
    balance = models.DecimalField(_('balance'), max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

