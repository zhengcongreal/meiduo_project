from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData

from apps.users.models import User


def generate_email_verify_url(user):
    """
          生成邮箱验证链接
          :param user: 当前登录用户
          :return: verify_url
          """
    s=Serializer(settings.SECRET_KEY,600)
    data={'user_id':user.id,'email':user.email}
    token=s.dumps(data).decode()
    url=settings.EMAIL_VERIFY_URL+token
    return url

def check_email_verify_url(token):
    """
            验证token并提取user
            :param token: 用户信息签名后的结果
            :return: user, None
            """
    # 调用 itsdangerous 类,生成对象
    # 邮件验证链接有效期：一天
    s = Serializer(settings.SECRET_KEY,600)
    try:
        data=s.loads(token)
    except BadData:
        # 如果传入的 token 中没有值, 则报错
        return None
    # 如果有值, 则获取
    else:
        user_id=data.get('user_id')
        email=data.get('email')
    try:
        user=User.objects.get(id=user_id,email=email)
    except  User.DoesNotExist:
        return None
    return user
