from starlette.requests import Request as StarletteRequest
from typing import Dict, Any, Optional, List, Union, AsyncGenerator
from contextvars import ContextVar

# 创建上下文变量来存储当前请求
_request_ctx_var: ContextVar[Optional[StarletteRequest]] = ContextVar('request', default=None)
# 创建上下文变量来缓存请求数据
_form_data_cache: ContextVar[Optional[Dict[str, Any]]] = ContextVar('form_data', default=None)
_json_data_cache: ContextVar[Optional[Dict[str, Any]]] = ContextVar('json_data', default=None)
# 创建上下文变量来存储g对象
_g_ctx_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar('g', default=None)
# 创建上下文变量来缓存文件数据
_files_cache: ContextVar[Optional[Dict[str, Any]]] = ContextVar('files', default=None)

class G:
    """Flask风格的g对象"""
    @property
    def _data(self) -> Dict[str, Any]:
        data = _g_ctx_var.get()
        if data is None:
            data = {}
            _g_ctx_var.set(data)
        return data
    
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(f'g对象没有属性: {name}')
    
    def __setattr__(self, name: str, value: Any) -> None:
        self._data[name] = value
    
    def __delattr__(self, name: str) -> None:
        if name in self._data:
            del self._data[name]
        else:
            raise AttributeError(f'g对象没有属性: {name}')
    
    def get(self, name: str, default: Any = None) -> Any:
        """获取属性，不存在则返回默认值"""
        return self._data.get(name, default)
    
    def pop(self, name: str, default: Any = None) -> Any:
        """移除并返回属性值"""
        return self._data.pop(name, default)
    
    def clear(self) -> None:
        """清空所有属性"""
        self._data.clear()
    
    def __contains__(self, name: str) -> bool:
        return name in self._data

# 创建全局g对象实例
g = G()

class RequestProxy:
    @property
    def request(self) -> Optional[StarletteRequest]:
        return _request_ctx_var.get()
    
    @property
    def method(self) -> str:
        if self.request:
            return self.request.method
        return ''
    
    @property
    def url(self) -> Any:
        if self.request:
            return self.request.url
        return None
    
    @property
    def path(self) -> str:
        if self.request:
            return self.request.url.path
        return ''
    
    @property
    def args(self) -> Dict[str, List[str]]:
        if self.request:
            return dict(self.request.query_params.multi_items())
        return {}
    
    async def form(self) -> Dict[str, Any]:
        """获取表单数据"""
        if not self.request:
            return {}
        
        # 检查缓存
        cached = _form_data_cache.get()
        if cached is not None:
            return cached
        
        # 解析表单数据
        try:
            form_data = await self.request.form()
            result = dict(form_data)
            # 缓存结果
            _form_data_cache.set(result)
            return result
        except Exception:
            return {}
    
    async def json(self) -> Dict[str, Any]:
        """获取JSON数据"""
        if not self.request:
            return {}
        
        # 检查缓存
        cached = _json_data_cache.get()
        if cached is not None:
            return cached
        
        # 解析JSON数据
        try:
            json_data = await self.request.json()
            # 缓存结果
            _json_data_cache.set(json_data)
            return json_data
        except Exception:
            return {}
    
    @property
    def cookies(self) -> Dict[str, str]:
        if self.request:
            return dict(self.request.cookies)
        return {}
    
    @property
    def headers(self) -> Dict[str, str]:
        if self.request:
            return dict(self.request.headers)
        return {}
    
    @property
    def environ(self) -> Dict[str, Any]:
        if self.request:
            return self.request.scope
        return {}
    
    @property
    async def files(self) -> Dict[str, Any]:
        """获取上传的文件"""
        if not self.request:
            return {}
        
        # 检查缓存
        from .request import _files_cache
        cached = _files_cache.get()
        if cached is not None:
            return cached
        
        # 解析表单数据，获取文件
        files = {}
        try:
            form_data = await self.request.form()
            for key, value in form_data.items():
                if hasattr(value, 'file') and hasattr(value, 'filename'):
                    # 创建Flask风格的文件对象
                    class FlaskFile:
                        def __init__(self, file_obj, filename):
                            self.file = file_obj
                            self.filename = filename
                            self.name = filename
                    
                    files[key] = FlaskFile(value.file, value.filename)
            
            # 缓存结果
            _files_cache.set(files)
        except Exception:
            pass
        
        return files
    
    @property
    def remote_addr(self) -> str:
        """获取客户端IP地址"""
        if self.request:
            return self.request.client.host if self.request.client else ''
        return ''
    
    @property
    def user_agent(self) -> str:
        """获取用户代理"""
        if self.request:
            return self.request.headers.get('user-agent', '')
        return ''
    
    @property
    def is_secure(self) -> bool:
        """检查是否为HTTPS请求"""
        if self.request:
            return self.request.url.scheme == 'https'
        return False
    
    @property
    def host(self) -> str:
        """获取主机名"""
        if self.request:
            return self.request.headers.get('host', '')
        return ''
    
    @property
    def base_url(self) -> str:
        """获取基础URL"""
        if self.request:
            return f"{self.request.url.scheme}://{self.request.headers.get('host', '')}"
        return ''
    
    @property
    def is_json(self) -> bool:
        """检查请求是否为JSON格式"""
        if self.request:
            content_type = self.request.headers.get('content-type', '')
            return 'application/json' in content_type
        return False
    
    @property
    def endpoint(self) -> str:
        """获取当前端点名称"""
        if self.request:
            return getattr(self.request, 'endpoint', None)
        return None
    
    @property
    def view_args(self) -> Dict[str, Any]:
        """获取视图参数"""
        if self.request:
            return getattr(self.request, 'path_params', {})
        return {}
    
    @property
    def blueprints(self) -> List[str]:
        """获取当前请求的蓝图"""
        # 简化实现，返回空列表
        return []
    
    @property
    def json(self) -> Dict[str, Any]:
        """获取JSON数据"""
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.get_json())
    
    def get_json(self, force: bool = False, silent: bool = False, cache: bool = True) -> Dict[str, Any]:
        """获取JSON数据"""
        import asyncio
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._get_json_async(force, silent, cache))
    
    async def _get_json_async(self, force: bool = False, silent: bool = False, cache: bool = True) -> Dict[str, Any]:
        """异步获取JSON数据"""
        if self.request:
            try:
                return await self.request.json()
            except Exception as e:
                if silent:
                    return {}
                raise
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取查询参数或表单数据"""
        if key in self.args:
            return self.args[key][0] if len(self.args[key]) > 0 else default
        return default
    
    def args_get(self, key: str, default: Any = None) -> Any:
        """获取查询参数"""
        if self.request:
            return self.request.query_params.get(key, default)
        return default
    
    async def form_get(self, key: str, default: Any = None) -> Any:
        """获取表单数据"""
        form_data = await self.form()
        return form_data.get(key, default)
    
    async def get_json(self, force: bool = False, silent: bool = False, cache: bool = True) -> Dict[str, Any]:
        """获取JSON数据"""
        if self.request:
            try:
                return await self.json()
            except Exception as e:
                if silent:
                    return {}
                raise
        return {}
    
    async def get_data(self, cache: bool = True, as_text: bool = False, parse_form_data: bool = False) -> Union[bytes, str, Dict[str, Any]]:
        """获取原始请求数据"""
        if self.request:
            data = await self.request.body()
            if as_text:
                return data.decode('utf-8')
            return data
        return b'' if not as_text else ''
    
    async def files_get(self, key: str, default: Any = None) -> Any:
        """获取上传的文件"""
        files = await self.files
        return files.get(key, default)

# 创建全局请求代理实例
request = RequestProxy()

# 用于设置当前请求的上下文管理器
class request_context:
    def __init__(self, req: StarletteRequest):
        self.req = req
        self.request_token = None
        self.form_token = None
        self.json_token = None
        self.g_token = None
        self.files_token = None
        self.session_token = None
        self.session_id_token = None
    
    async def __aenter__(self):
        self.request_token = _request_ctx_var.set(self.req)
        self.form_token = _form_data_cache.set(None)
        self.json_token = _json_data_cache.set(None)
        self.g_token = _g_ctx_var.set({})
        self.files_token = _files_cache.set(None)
        # 导入会话相关的上下文变量
        from .utils import _session_ctx_var, _session_id_ctx_var
        self.session_token = _session_ctx_var.set({})
        self.session_id_token = _session_id_ctx_var.set(None)
        return self.req
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.request_token:
            _request_ctx_var.reset(self.request_token)
        if self.form_token:
            _form_data_cache.reset(self.form_token)
        if self.json_token:
            _json_data_cache.reset(self.json_token)
        if self.g_token:
            _g_ctx_var.reset(self.g_token)
        if self.files_token:
            _files_cache.reset(self.files_token)
        # 重置会话相关的上下文变量
        from .utils import _session_ctx_var, _session_id_ctx_var
        if self.session_token:
            _session_ctx_var.reset(self.session_token)
        if self.session_id_token:
            _session_id_ctx_var.reset(self.session_id_token)

# 请求代理，用于兼容Flask的request对象使用方式
request_proxy = request
