from django.urls import path
from myapp import views

urlpatterns = [
    path('my-model/', views.MyView.as_view())
]
