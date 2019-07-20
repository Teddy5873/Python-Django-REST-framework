from django.shortcuts import render

# Create your views here.
from rest_framework import mixins
from rest_framework import status
from rest_framework.decorators import action

from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import constants
from users import serializers
from users.models import User



class UserView(CreateAPIView):
    serializer_class = serializers.CreateUserSerializer


class UsernameCountView(APIView):
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        data = {
            'username':username,
            'count':count
        }
        return Response(data)


class MobileCountView(APIView):

    def get(self, request, mobile):

        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# GET /user/
class UserDetailView(RetrieveAPIView):
    """用户基本信息"""
    serializer_class = serializers.UserDetailSerializer
    permission_classes = [IsAuthenticated]  # 指明必须登录认证后才能访问


    def get_object(self):
        # 返回当前请求的用户
        # 在类视图对象中，可以通过类视图对象的属性获取request
        # 在django的请求request对象中，user属性表明当请请求的用户
        return self.request.user



class EmailView(UpdateAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.check_verify_email_token(token)

        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class AddressViewSet(mixins.CreateModelMixin,mixins.UpdateModelMixin,GenericViewSet):
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted  = False)

    def list(self,request,*args,**kwargs):

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset,many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self,request,*args,**kwargs):
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request,*args,**kwargs)


    def destroy(self,request,*args,**kwargs):
        address = self.get_object()

        address.is_deleted = True
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)














