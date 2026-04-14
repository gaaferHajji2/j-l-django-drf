from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ('view_categories', 'can view categories')
        ]

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='my_products')

    class Meta:
        permissions = [
            ('manage_products', 'can manage products')
        ]