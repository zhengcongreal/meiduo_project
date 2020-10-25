from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,BadData
def generate_access_token_openid(openid):
    '''
    序列化openid
    :param openid:
    :return:
    '''
    # 创建序列化器对象
    s=Serializer(settings.SECRET_KEY,600)
    # 构造要序列化的数据
    data={'openid':openid}
    # 序列化
    token=s.dumps(data)
    # 返回密文字符串：将bytes类型的token转成字符串类型的数据

    return token.decode()




def check_access_token_openid(access_token):
    """
        反序列化openid
        :param access_token: 密文字符串
        :return: 明文
        """
    # 创建序列化器对象
    s=Serializer(settings.SECRET_KEY,600)
    # 反序列化
    try:
        data=s.loads(access_token)
    except BadData:
        return  None
    # 读取openid明文
    openid=data.get('openid')
    # 返回openid明文
    return openid