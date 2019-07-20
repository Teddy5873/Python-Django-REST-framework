from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.exceptions import OAuthQQAPIError
from oauth.models import OAuthQQUser
from oauth.serializers import OAuthQQUserSerializer
from oauth.utils import OAuthQQ


class QQAuthURLView(APIView):
    def get(self,request):
        next = request.query_params.get('next')
        oauth = OAuthQQ(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({'login_url':login_url})


class QQAuthUserView(CreateAPIView):
    serializer_class = OAuthQQUserSerializer


    def get(self,request):
        code = request.query_params.get('code')

        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            openid = oauth_qq.get_openid(access_token)

        except OAuthQQAPIError:
            return Response({'message': '访问QQ接口异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        try:
            oauth_qq_user = OAuthQQUser.objects.get(openid = openid)
        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在，处理openid 并返回
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({'access_token': access_token})
        else:

            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'username': user.username,
                'user_id': user.id,
                'token': token
            })






