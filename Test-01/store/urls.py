# from django.urls import path

# from rest_framework.routers import SimpleRouter

from rest_framework_nested import routers

# from pprint import pprint

from . import views

router = routers.DefaultRouter() # type: ignore

router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
router.register('orders', views.OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-reviews')
products_router.register('images', views.ProductImageViewSet, basename='product-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# pprint(router.urls)

# urlpatterns = [
    # path('product/', views.ProductList.as_view()),
    # path('product/<int:pk>/', views.ProductDetail.as_view()),

    # path('collection/<int:pk>/', views.collection_detail, name='collection-detail')

    # path('collection/', views.CollectionList.as_view()),

    # path('collection/<int:pk>/', views.CollectionDetail.as_view())
# ];

urlpatterns = router.urls + products_router.urls + carts_router.urls