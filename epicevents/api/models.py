
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, PermissionsMixin
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
 

class UserManager(BaseUserManager):
    def create_user(self, username, role, password=None):
        if not username:
            raise ValueError("Users must have an username")
        user = self.model(
            username=username,
            role=role
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username,
            role='manager',
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('seller', 'Seller'),
        ('support', 'Support'),
        ('manager', 'Manager'),
    )
    username = models.CharField(max_length=100, unique=True)
    role = models.CharField(choices=ROLE_CHOICES, default='manager', max_length=7)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELD = ['role']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app 'app_label "
        return True
    
    @property
    def is_staff(self):
        return True if self.role == 'manager' else False


class Client(models.Model):
    ROLE_CHOICES = (
        ('prospect', 'Prospect'),
        ('client', 'Client'),
    )
    firstname = models.CharField(max_length=25)
    lastname = models.CharField(max_length=25)
    email = models.EmailField(max_length=200, unique=True)
    phone = models.CharField(max_length=10, blank=True)
    mobile = models.CharField(max_length=10, unique=True)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default='client')
    company_name = models.CharField(max_length=250, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    sale_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='clients', null=True, blank=True)

    def __str__(self):
        return self.email


class Contract(models.Model):
    STATUS_CHOICE = (
        ('signed', 'Signed'),
        ('unsigned', 'Unsigned'),
        ('ended', 'Ended')
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICE, default='unsigned',max_length=8)
    amount = models.FloatField()
    payment_due = models.DateField(blank=True, null=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='contracts')
    sales_contact = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='contracts', null=True)

    def __str__(self):
        return f"contract '{self.status}' of {self.client}"


class Event(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    attendees = models.IntegerField()
    event_date = models.DateField()
    notes = models.TextField(max_length=3000)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='events')
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='events')
    support_contact = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='events', null=True)


