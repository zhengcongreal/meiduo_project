# 自定义文件存储类，提供文件下载的全路径
from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储类"""

    def _open(self, name, mode='rb'):
        """
        打开文件时自动调用的，而当前不是打开文件，但是文档告诉我又必须实现，我也不知道写什么，所以pass
        :param name: 要打开的文件的名字
        :param mode: 打开文件的模式
        :return: None
        """
        pass

    def _save(self, name, content):
        """
        保存文件时自动调用的，而当前不是保存文件，但是文档告诉我又必须实现，我也不知道写什么，所以pass
        :param name: 要保存的文件的名字
        :param content: 要保存的文件的内容
        :return: None
        """
        pass

    def url(self, name):
        """
        返回文件下载全路径的方法
        :param name: 外界的image字段传入到文件名：file_id=group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396
        :return: http://192.168.103.100:8888/group1/M00/00/01/CtM3BVrLmc-AJdVSAAEI5Wm7zaw8639396
        """
        # return 'http://192.168.103.100:8888/' + name
        # return 'http://image.meiduo.site:8888/' + name
        return settings.FDFS_URL + name