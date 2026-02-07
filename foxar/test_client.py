from fastapi.testclient import TestClient
from typing import Optional, Dict, Any, Union, ContextManager, List

class SessionTransaction:
    """会话事务类"""
    def __init__(self, client):
        self.client = client
        self.session_data = {}
        self._initial_session = {}
    
    def __enter__(self):
        # 获取当前会话数据
        if 'session_id' in self.client.cookies:
            # 这里可以添加从服务器获取会话数据的逻辑
            pass
        self._initial_session = self.session_data.copy()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 提交会话数据
        if self.session_data != self._initial_session:
            # 这里可以添加将会话数据发送到服务器的逻辑
            pass
    
    def __setitem__(self, key, value):
        self.session_data[key] = value
    
    def __getitem__(self, key):
        return self.session_data[key]
    
    def __delitem__(self, key):
        del self.session_data[key]
    
    def __contains__(self, key):
        return key in self.session_data
    
    def get(self, key, default=None):
        return self.session_data.get(key, default)
    
    def pop(self, key, default=None):
        return self.session_data.pop(key, default)
    
    def clear(self):
        self.session_data.clear()
    
    def keys(self):
        return self.session_data.keys()
    
    def values(self):
        return self.session_data.values()
    
    def items(self):
        return self.session_data.items()
    
    def update(self, *args, **kwargs):
        self.session_data.update(*args, **kwargs)
    
    def setdefault(self, key, default=None):
        return self.session_data.setdefault(key, default)

class FlaskResponse:
    """兼容Flask的响应类"""
    def __init__(self, response):
        self.response = response
    
    @property
    def status_code(self):
        return self.response.status_code
    
    @property
    def headers(self):
        return self.response.headers
    
    @property
    def cookies(self):
        return self.response.cookies
    
    @property
    def data(self):
        return self.response.content
    
    @property
    def text(self):
        return self.response.text
    
    def json(self):
        return self.response.json()
    
    def get_data(self, as_text=False):
        if as_text:
            return self.response.text
        return self.response.content
    
    def get_json(self, force=False, silent=False):
        try:
            return self.response.json()
        except Exception as e:
            if silent:
                return None
            raise

class TestClient(TestClient):
    """兼容Flask的测试客户端"""
    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        self.test_client_class = self.__class__
        self.application = app
    
    def get(self, path, **kwargs):
        """发送GET请求"""
        response = super().get(path, **kwargs)
        return FlaskResponse(response)
    
    def post(self, path, data=None, json=None, **kwargs):
        """发送POST请求"""
        response = super().post(path, data=data, json=json, **kwargs)
        return FlaskResponse(response)
    
    def put(self, path, data=None, **kwargs):
        """发送PUT请求"""
        response = super().put(path, data=data, **kwargs)
        return FlaskResponse(response)
    
    def delete(self, path, **kwargs):
        """发送DELETE请求"""
        response = super().delete(path, **kwargs)
        return FlaskResponse(response)
    
    def patch(self, path, data=None, **kwargs):
        """发送PATCH请求"""
        response = super().patch(path, data=data, **kwargs)
        return FlaskResponse(response)
    
    def head(self, path, **kwargs):
        """发送HEAD请求"""
        response = super().head(path, **kwargs)
        return FlaskResponse(response)
    
    def options(self, path, **kwargs):
        """发送OPTIONS请求"""
        response = super().options(path, **kwargs)
        return FlaskResponse(response)
    
    # 添加Flask测试客户端特有的方法
    def post_json(self, path, data=None, **kwargs):
        """发送JSON POST请求"""
        response = super().post(path, json=data, **kwargs)
        return FlaskResponse(response)
    
    def put_json(self, path, data=None, **kwargs):
        """发送JSON PUT请求"""
        response = super().put(path, json=data, **kwargs)
        return FlaskResponse(response)
    
    def patch_json(self, path, data=None, **kwargs):
        """发送JSON PATCH请求"""
        response = super().patch(path, json=data, **kwargs)
        return FlaskResponse(response)
    
    def post_form(self, path, data=None, **kwargs):
        """发送表单POST请求"""
        response = super().post(path, data=data, **kwargs)
        return FlaskResponse(response)
    
    def get_json(self, path, **kwargs):
        """发送GET请求并返回JSON响应"""
        response = super().get(path, **kwargs)
        return response.json()
    
    def session_transaction(self, **kwargs) -> ContextManager[SessionTransaction]:
        """开始会话事务"""
        return SessionTransaction(self)
    
    def test_request_context(self, *args, **kwargs):
        """创建测试请求上下文"""
        # 简化实现，返回一个空的上下文管理器
        class MockContext:
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
        return MockContext()
    
    def test_client(self, **kwargs):
        """创建新的测试客户端"""
        return self.__class__(self.application, **kwargs)
    
    @property
    def cookies(self):
        """获取cookies"""
        return super().cookies
    
    @property
    def headers(self):
        """获取headers"""
        return super().headers
    
    @property
    def path(self):
        """获取当前路径"""
        return ""
    
    def __enter__(self):
        """进入上下文管理器"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器"""
        self.close()
    
    def close(self):
        """关闭测试客户端"""
        super().close()