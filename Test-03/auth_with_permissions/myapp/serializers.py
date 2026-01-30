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