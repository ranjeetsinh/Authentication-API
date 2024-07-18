import random
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer, OTPSerializer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .utils import generate_otp
from django.contrib.auth.hashers import make_password,  check_password
import string

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful. Please verify your email."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RequestOTPView(APIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'error': 'User not found'}, status=404)

            otp = generate_otp()
            user.otp = make_password(otp)  # Hashing the OTP before storing
            user.save()

            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp}',
                'no-reply@example.com',
                [email],
                fail_silently=False,
            )

            return Response({'message': 'OTP sent to your email.'}, status=200)
        else:
            return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({'error': 'User not found'}, status=404)

            if not check_password(otp, user.otp):
                return Response({'error': 'Invalid OTP'}, status=400)

            # Generating JWT token for the user
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful.',
                'token': str(refresh.access_token)
            }, status=200)
        else:
            return Response(serializer.errors, status=400)