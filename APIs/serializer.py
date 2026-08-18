from rest_framework import serializers
from members.models import Member
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class MemberSerializer(serializers.ModelSerializer):
    member_id = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = Member
        fields = [
            "member_id",
            "firebase_uid",
            "name",
            "email",
            "deadline",
            "account_status",
            "is_activated",
            "trainee_code",
            "workout_days",
            "meals_num",
        ]


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)

    def validate(self, attrs):
        password = attrs.get("password")
        email = attrs.get("email")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError("Invalid email or password")

        refresh = self.get_token(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }