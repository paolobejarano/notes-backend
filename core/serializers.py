from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Note, Category


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True}
        }
    
    def validate_email(self, value):
        # Standardize email: lowercase and strip whitespace
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Standardize email: lowercase and strip whitespace
            email = email.strip().lower()
            try:
                user = User.objects.get(email=email)
                
                # Check if user is active before authentication
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                
                authenticated_user = authenticate(username=user.username, password=password)
                if authenticated_user is None:
                    raise serializers.ValidationError('Invalid email or password.')
                
                attrs['user'] = authenticated_user
                return attrs
                
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid email or password.')
        else:
            raise serializers.ValidationError('Must include email and password.')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']


class TokensSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()


class AuthResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserSerializer()
    tokens = TokensSerializer()


class CategorySerializer(serializers.ModelSerializer):
    note_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'color', 'note_count']
    
    def get_note_count(self, obj):
        # Get the request from context to filter by current user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Note.objects.filter(
                category=obj,
                user=request.user,
                deleted_at__isnull=True
            ).count()
        return 0


class NoteSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'body', 'category', 'category_id', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_category_id(self, value):
        try:
            Category.objects.get(id=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError("Category does not exist.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'body', 'category']
        
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'body', 'category']
