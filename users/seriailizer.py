from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re



from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

class UserRegisterSerializer(serializers.ModelSerializer):


    email = serializers.EmailField(
        required=True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )

    phone_number = serializers.CharField(
        required=False,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    otp_register = serializers.BooleanField(required=True)


    class Meta:
        model = User
        fields = ['email','password','otp_register','first_name', 'last_name', 'phone_number']

   

    def create(self, validated_data):
        validated_data.pop('otp_register',None)
        email = validated_data.get('email', '')
        validated_data['username'] = email
        user = User.objects.create_user(**validated_data)
        return user




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['first_name'] = getattr(user, 'first_name', None)
        token['email'] = user.email
        token['last_name'] = user.last_name
        token['phone_number'] = getattr(user, 'phone_number', None)
        token['user_id'] = str(user.id)


        return token




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Include fields you want to expose in API
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'date_joined',
            'is_active',
            'groups',
            'user_permissions',
        ]
        read_only_fields = ['email']  # Make email read-only

    # Optional: display groups and permissions as list of names instead of IDs
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=User.groups.through.objects.all()  # or Group.objects.all()
    )

    user_permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=User.user_permissions.through.objects.all()  # or Permission.objects.all()
    )


    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should contain only letters.")
        return value

    def validate_last_name(self, value):
        if value:  
            if not value.isalpha():
                raise serializers.ValidationError("Last name should contain only letters.")
        return value

    def validate_phone_number(self, value):
        if not value:
            return value  

        if not re.fullmatch(r'\d{10}', value):
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value
