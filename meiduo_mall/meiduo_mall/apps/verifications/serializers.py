from django_redis import get_redis_connection
from rest_framework import serializers


class ImageCodeCheckSerializer(serializers.Serializer):

    image_code_id = serializers.UUIDField(required=True)
    text = serializers.CharField(max_length = 4, min_length = 4, required=True)

    def validate(self, attrs):
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        redis_conn.delete('img_%s' % image_code_id)

        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != text.lower():
            raise serializers.ValidationError('图片验证码错误')

        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('请求过于频繁')

        return attrs
