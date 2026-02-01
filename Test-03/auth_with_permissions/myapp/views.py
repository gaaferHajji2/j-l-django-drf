from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, ProductSerializer, CategorySerializer, CreateCustomerSerializer
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import Product, Category, CustomUser
from .permissions import CanManageProducts, CanViewCategories, IsOwnerOrReadOnly

class RegisterView(APIView):
    permission_classes = []  # No auth required
    serializer_class = CreateCustomerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            return Response({
                'message': 'User created successfully.',
                'user_id': user.id,
                'email': user.email,
                'username': user.username,
                'phone_number': user.phone_number.__str__(),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.
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

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [CanManageProducts]

    def get_serializer_context(self):
        return { "request": self.request }

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_context(self):
        return { "request": self.request }

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CanViewCategories]

    def get_serializer_context(self):
        return { "request": self.request }

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_context(self):
        return { "request": self.request }

class ManageUserPermissionsView(APIView):
    def post(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            permission_codename = request.data.get('permission')
            action = request.data.get('action')  # 'add' or 'remove'
            model_name = request.data.get('model_name')

            if model_name == 'Product':
                model_value = Product
            elif model_name == 'Category':
                model_value = Category
            else:
                return Response({ 'status': 'Model Not Valid' }, status=400)
            
            content_type = ContentType.objects.get_for_model(model_value)
            print("The content type is: ", content_type.id)
            print("The permission codename is: ", permission_codename)
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
        except Permission.DoesNotExist:
            return Response({'error': 'Invalid permission'}, status=400)
        except CustomUser.DoesNotExist:
            return Response({'error': "No User Found"}, status=400)

class UserAPIView(APIView):
    def get(self, request):
        return CustomUser.objects.select_related('profile').filter(CustomUser__id = request.user.id)