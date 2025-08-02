from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EBooklet, UserEBookletSelection

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    memberID = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone_number', 'memberID')

    def create(self, validated_data):
        memberID = validated_data.pop('memberID', None)
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data.get('phone_number', ''),
            memberID=memberID
        )
        # You can handle memberID here if you want to store it or process it
        user.set_password(validated_data['password'])
        user.save()
        return user

class EBookletSerializer(serializers.ModelSerializer):
    class Meta:
        model = EBooklet
        fields = ('id', 'name', 'pdf_file')

class UserEBookletSelectionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    ebooklet = serializers.PrimaryKeyRelatedField(queryset=EBooklet.objects.all())

    class Meta:
        model = UserEBookletSelection
        fields = ('id', 'user', 'ebooklet', 'payment_verified', 'approved', 'selected_at')
