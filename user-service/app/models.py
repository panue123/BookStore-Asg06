from django.db import models


class UserRole(models.TextChoices):
    MANAGER = 'manager', 'Manager'
    STAFF = 'staff', 'Staff'
    CUSTOMER = 'customer', 'Customer'


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street}, {self.city}"


class Job(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title} @ {self.company}"


class UserAccount(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    department = models.CharField(max_length=100, blank=True, default='')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    cart_id = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.role})"
