from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from store.signals import order_created

from .models import (
    CartItem,
    Customer,
    Order,
    OrderItem,
    Product,
    Collection,
    ProductImage,
    Review,
    Cart,
)

from core.serializers import UserSerializer

# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length= 255)

# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
#     price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')

#     # collection = serializers.PrimaryKeyRelatedField(queryset = Collection.objects.all())

#     # collection = serializers.StringRelatedField()
#     # collection = CollectionSerializer()

#     collection = serializers.HyperlinkedRelatedField(
#         queryset = Collection.objects.all(),
#         view_name = 'collection-detail',
#     )

#     def calculate_tax(self, product: Product):
#         return product.unit_price * Decimal(1.1)


class CollectionSerializer(serializers.ModelSerializer):

    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]

    # products_count = serializers.SerializerMethodField(method_name='get_products_count')

    # def get_products_count(self, collection: Collection):
    #     return collection.products_count


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "inventory",
            "unit_price",
            "price_with_tax",
            "collection",
        ]

    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')

    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ["id", "name", "description", "date"]

    def create(self, validated_data):
        product_id = self.context["product_id"]

        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerialzier()

    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])  # type: ignore

    class Meta:
        model = Cart
        # Here We Define items Inside The CartItem-Model AS The Related Name
        fields = ["id", "items", "total_price"]


class AddCartItemSerialzier(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    product_id = serializers.IntegerField()  # Here we set product_id
    # because it is populated only in runtime

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(f"No product found with value: {value}")
        return value

    # here will call self.is_valid
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data["product_id"]  # type: ignore
        quantity = self.validated_data["quantity"]  # type: ignore

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()

            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)  # type: ignore

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership", "user"]


class SimpleCustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerialzier()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    customer = SimpleCustomerSerializer(read_only=True)
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "customer", "items"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(detail="Cart Not Found" )

        if CartItem.objects.filter(cart_id = cart_id).count() == 0 :
            raise serializers.ValidationError("No CartItems found for this cart")

        return cart_id

    def save(self, **kwargs):
        # print(self.validated_data["cart_id"])  # type: ignore
        # print(self.context["user_id"])
        # print(self.context["is_staff"])

        customer, _ = Customer.objects.get_or_create(user_id=self.context["user_id"])

        with transaction.atomic():
            order = Order.objects.create(customer=customer)

            cartItems = CartItem.objects.select_related("product").filter(cart_id=self.validated_data["cart_id"])  # type: ignore

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price,
                )
                for item in cartItems
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk = self.validated_data['cart_id']).delete() # type: ignore

            print(self.__class__)
            
            order_created.send_robust(self.__class__, order=order)

            return order

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields= ['id', 'image']