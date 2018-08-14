from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from dailyfresh import settings

class FDfsStorage(Storage):
    """自定义存储类"""
    def __init__(self,client_conf=None,nginx_url=None):
        # 初始化实例对象
        if client_conf is None:
            client_conf=settings.FDFS_CLIENT_CONF
        self.client_conf=client_conf
        if nginx_url is None:
            nginx_url=settings.FDFS_NGINX_URL
        self.nginx_url=nginx_url

    def _save(self,name,content):
        """保存文件时调用"""
        # 1.保存文件到fdfs系统
        client=Fdfs_client(self.client_conf)
        file_content=content.read()
        response=client.upload_by_buffer(file_content)
        # 2.判断文件是否上传成功
        if response is None or response.get('Status')!='Upload successed.':
            raise Exception('上传文件到fast dfs系统失败！')
        # 3.上传成功返回文件的id
        file_id=response.get('Remote file_id')
        return file_id

    def exists(self,name):
        """判断文件是否存在，因为fdfs系统存放的文件名永远不会相同，所以就不会存在文件相同，直接return False"""
        return False

    def url(self, name):
        """返回可访问到文件的url地址:http://ip:nginx端口号/name"""
        return self.nginx_url+name