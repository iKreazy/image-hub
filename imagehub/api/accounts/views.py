from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AccountSerializer, SignUpSerializer, AccountSettingsSerializer


class AccountInfoView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def get(self, request, *args, **kwargs):
        serializer = AccountSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class AccountSignUpView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = get_user_model().objects.get(username=response.data['username'])
        return Response(AccountSerializer(user, context={'request': request}).data, status=status.HTTP_201_CREATED)


class AccountSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = AccountSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Method 'GET' not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            password_updated = 'password1' in serializer.validated_data

            self.perform_update(serializer)

            if password_updated:
                return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

            serializer = AccountSerializer(instance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer

    def delete(self, request, *args, **kwargs):
        user = request.user
        if user.avatar:
            user.avatar.delete(save=False)
        user.delete()
        return Response({"detail": "Account successfully deleted."}, status=status.HTTP_204_NO_CONTENT)
