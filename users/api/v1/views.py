from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.api.v1.serializers import UserSerializer, UserLoginDataSerializer, LoginSerializer

User = get_user_model()


class UserResource(ModelViewSet):
    http_method_names = ['post', 'get', 'patch', 'put', 'head']
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_superuser=False, is_staff=False, is_active=True).order_by('-created_at')

    def get_queryset(self):
        return User.objects.filter(
            is_superuser=False, is_staff=False, is_active=True, pk=self.request.user.pk
        ).order_by('-created_at')

    def get_permissions(self):
        if self.action in ['create', ]:
            self.permission_classes = []
            self.authentication_classes = []
        return super(UserResource, self).get_permissions()

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = UserLoginDataSerializer(user, many=False, context={'request': request}).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class LoginAPIView(GenericAPIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = authenticate(request=request, username=data['username'], password=data['password'])
        if user:
            return Response({
                'data': UserLoginDataSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)

        raise AuthenticationFailed()
