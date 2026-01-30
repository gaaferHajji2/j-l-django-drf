Here's a comprehensive example for a Django REST Framework (DRF) project that meets all your requirements:

---

### 1. **Project Setup & Dependencies**

Install required packages:
```bash
pip install djangorestframework djangorestframework-simplejwt django-phonenumber-field[phonenumbers]
```

Add to `settings.py`:
```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'phonenumber_field',
    'myapp',  # Your app name
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

---

### 2. **Custom User Model**
```python
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)

# Signals for auto-creating profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

---

### 3. **Custom Permissions**
```python
# permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class CanManageProducts(permissions.BasePermission):
    message = "You don't have permission to manage products."

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.manage_products')

class CanViewCategories(permissions.BasePermission):
    message = "You need category viewing permission."

    def has_permission(self, request, view):
        return request.user.has_perm('myapp.view_categories')
```

---

### 4. **Custom Validation Messages**
```python
# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, Profile

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False)
    
    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone_number')
        
        if not email and not phone:
            raise serializers.ValidationError(
                "Either email or phone number is required."
            )
        
        # Try to find user by email or phone
        try:
            if email:
                user = CustomUser.objects.get(email=email)
            else:
                user = CustomUser.objects.get(phone_number=phone)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with provided credentials."
            )
        
        # Verify credentials
        if not user.check_password(attrs.get('password', '')):
            raise serializers.ValidationError(
                "Invalid password."
            )
            
        attrs['user'] = user
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'profile']
    
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        profile = instance.profile
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance
```

---

### 5. **JWT Login View**
```python
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer

class LoginView(APIView):
    permission_classes = []
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

---

### 6. **Models for Products & Categories**
```python
# models.py (continued)
class Category(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
```

---

### 7. **Views with Custom Permissions**
```python
# views.py (continued)
from rest_framework import generics, permissions
from .models import Product, Category
from .permissions import CanManageProducts, CanViewCategories, IsOwnerOrReadOnly

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [CanManageProducts]

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CanViewCategories]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrReadOnly]
```

---

### 8. **Permission Management Endpoint**
```python
# views.py (continued)
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

class ManageUserPermissionsView(APIView):
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            permission_codename = request.data.get('permission')
            action = request.data.get('action')  # 'add' or 'remove'
            
            content_type = ContentType.objects.get_for_model(Product)
            permission = Permission.objects.get(
                codename=permission_codename,
                content_type=content_type
            )
            
            if action == 'add':
                user.user_permissions.add(permission)
                return Response({'status': 'Permission added'})
            elif action == 'remove':
                user.user_permissions.remove(permission)
                return Response({'status': 'Permission removed'})
            else:
                return Response({'error': 'Invalid action'}, status=400)
                
        except (CustomUser.DoesNotExist, Permission.DoesNotExist):
            return Response({'error': 'Invalid user or permission'}, status=400)
```

---

### 9. **URL Configuration**
```python
# urls.py
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('products/', views.ProductListCreateView.as_view()),
    path('products/<int:pk>/', views.ProductDetailView.as_view()),
    
    path('categories/', views.CategoryListView.as_view()),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view()),
    
    path('manage-permissions/<int:user_id>/', views.ManageUserPermissionsView.as_view()),
]
```

---

### Key Features Implemented:

1. **JWT Authentication**  
   - Login accepts email OR phone number
   - Returns JWT tokens on successful authentication

2. **Custom Permissions**  
   - `CanManageProducts`: Checks for `myapp.manage_products` permission
   - `CanViewCategories`: Checks for `myapp.view_categories` permission
   - `IsOwnerOrReadOnly`: Object-level ownership check

3. **Dynamic Permission Management**  
   - `ManageUserPermissionsView` allows adding/removing permissions via API
   - Uses Django's built-in permission system

4. **Custom Validation Messages**  
   - Clear error messages in `LoginSerializer`
   - Handles both email and phone authentication

5. **Profile Module with Signals**  
   - Auto-created `Profile` on user creation
   - Nested serialization in `UserSerializer`

6. **Authorization for Endpoints**  
   - All product/category endpoints require authentication
   - Specific permissions required for different operations

---

### Usage Examples:

**Login Request:**
```json
POST /login/
{
  "email": "user@example.com",
  "password": "secret"
}
```

**Add Permission to User:**
```json
POST /manage-permissions/1/
{
  "permission": "manage_products",
  "action": "add"
}
```

**Get User Profile:**
```http
GET /users/1/
Authorization: Bearer <access_token>
```

This implementation provides a complete, secure system with flexible permission management and proper validation handling.