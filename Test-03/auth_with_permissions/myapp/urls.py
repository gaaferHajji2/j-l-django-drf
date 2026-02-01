from django.urls import path
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
    path('user/', views.UserAPIView.as_view()),
    path('customer/', views.RegisterView.as_view()),
]
