from typing import Any, Dict, List, Optional, Callable
from urllib.parse import urlencode

class Config(dict):
    """兼容Flask的配置类"""
    def __init__(self, root_path: str = "", defaults: Optional[Dict[str, Any]] = None):
        super().__init__(defaults or {})
        self.root_path = root_path
        # 设置默认配置
        self.set_defaults()
    
    def set_defaults(self) -> None:
        """设置默认配置"""
        # Flask风格的默认配置
        self.setdefault('DEBUG', False)
        self.setdefault('TESTING', False)
        self.setdefault('SECRET_KEY', None)
        self.setdefault('PERMANENT_SESSION_LIFETIME', 31536000)  # 1年
        self.setdefault('USE_X_SENDFILE', False)
        self.setdefault('SERVER_NAME', None)
        self.setdefault('APPLICATION_ROOT', '/')
        self.setdefault('PREFERRED_URL_SCHEME', 'http')
        self.setdefault('MAX_CONTENT_LENGTH', None)
        self.setdefault('SEND_FILE_MAX_AGE_DEFAULT', 43200)  # 12小时
        self.setdefault('TRAP_BAD_REQUEST_ERRORS', None)
        self.setdefault('TRAP_HTTP_EXCEPTIONS', False)
        self.setdefault('EXPLAIN_TEMPLATE_LOADING', False)
        self.setdefault('PRESERVE_CONTEXT_ON_EXCEPTION', None)
        self.setdefault('TEMPLATES_AUTO_RELOAD', None)
        self.setdefault('MAX_COOKIE_SIZE', 4093)
    
    def from_object(self, obj: Any) -> None:
        """从对象加载配置"""
        if isinstance(obj, str):
            import importlib
            mod = importlib.import_module(obj)
            obj = mod
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)
    
    def from_pyfile(self, filename: str, silent: bool = False) -> bool:
        """从Python文件加载配置"""
        import os
        import sys
        import types
        
        filename = os.path.join(self.root_path, filename)
        if not os.path.exists(filename):
            if silent:
                return False
            raise OSError(f"Config file not found: {filename}")
        
        d = types.ModuleType('config')
        d.__file__ = filename
        try:
            with open(filename, 'rb') as f:
                exec(compile(f.read(), filename, 'exec'), d.__dict__)
        except Exception as e:
            if silent:
                return False
            raise
        
        self.from_object(d)
        return True
    
    def from_envvar(self, variable_name: str, silent: bool = False) -> bool:
        """从环境变量加载配置文件路径"""
        import os
        
        filename = os.environ.get(variable_name)
        if not filename:
            if silent:
                return False
            raise RuntimeError(f"Environment variable {variable_name} not set")
        
        return self.from_pyfile(filename, silent=silent)
    
    def from_mapping(self, *mapping, **kwargs) -> None:
        """从映射加载配置"""
        mappings = []
        if mapping:
            mappings.extend(mapping)
        if kwargs:
            mappings.append(kwargs)
        
        for mapping in mappings:
            if not isinstance(mapping, dict):
                raise TypeError('mapping must be a dict')
            for key, value in mapping.items():
                if key.isupper():
                    self[key] = value
    
    def from_prefixed_env(
        self, 
        prefix: str = "FLASK_", 
        loads: Optional[Callable[[str], Any]] = None
    ) -> bool:
        """从带前缀的环境变量加载配置"""
        import os
        
        if loads is None:
            import ast
            def loads(value):
                try:
                    return ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    return value
        
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            
            # 移除前缀并转换为大写
            config_key = key[len(prefix):].upper()
            self[config_key] = loads(value)
        
        return True
    
    def get_namespace(self, namespace: str, lowercase: bool = False, trim_namespace: bool = True) -> Dict[str, Any]:
        """获取指定命名空间的配置"""
        rv = {}
        prefix = namespace + '_'
        
        for key, value in self.items():
            if not key.startswith(prefix):
                continue
            if trim_namespace:
                key = key[len(prefix):]
            if lowercase:
                key = key.lower()
            rv[key] = value
        
        return rv
    
    def validate(self) -> None:
        """验证配置"""
        # 检查必要的配置
        if self.get('SECRET_KEY') is None and not self.get('TESTING'):
            import warnings
            warnings.warn(
                "The SECRET_KEY configuration is not set. "
                "This is dangerous and should be set in production.",
                RuntimeWarning
            )
        
        # 检查DEBUG模式
        if self.get('DEBUG') and self.get('TESTING'):
            import warnings
            warnings.warn(
                "DEBUG is True in testing mode. "
                "This may lead to unexpected behavior.",
                RuntimeWarning
            )
    
    def __repr__(self) -> str:
        """返回配置的字符串表示"""
        return f"<Config {dict(self)}>"

# 全局路由映射
_route_map: Dict[str, str] = {}

def register_route(endpoint: str, path: str) -> None:
    """注册路由到全局映射"""
    _route_map[endpoint] = path

def url_for(
    endpoint: str,
    **values: Any
) -> str:
    """生成URL"""
    # 处理静态文件URL
    if endpoint == 'static':
        filename = values.get('filename')
        if filename:
            static_url = "/static"
            # 构建静态文件路径
            if not filename.startswith("/"):
                filename = "/" + filename
            path = static_url + filename
            
            # 添加查询参数
            del values['filename']
            if values:
                path += "?" + urlencode(values)
            
            return path
    
    # 从路由映射中获取路径
    if endpoint in _route_map:
        path = _route_map[endpoint]
    else:
        # 如果没有找到，使用简化实现
        path = f"/{endpoint}"
    
    # 替换路径中的参数
    for key, value in values.items():
        if f"<{key}>" in path:
            path = path.replace(f"<{key}>", str(value))
            del values[key]
        elif f"<{key}:" in path:
            # 处理带类型的参数
            import re
            pattern = re.compile(f"<{key}:[^>]+>")
            path = pattern.sub(str(value), path)
            del values[key]
    
    # 添加查询参数
    if values:
        path += "?" + urlencode(values)
    
    return path

# 添加flash消息支持（简化实现）
_flash_messages: List[Dict[str, Any]] = []

def flash(message: str, category: str = "message") -> None:
    """添加flash消息"""
    _flash_messages.append({"message": message, "category": category})
    
    # 发送消息闪现信号
    try:
        from .signals import message_flashed
        message_flashed.send(None, message=message, category=category)
    except ImportError:
        pass

def get_flashed_messages(with_categories: bool = False, category_filter: Optional[List[str]] = None) -> List[Any]:
    """获取flash消息"""
    global _flash_messages
    messages = _flash_messages.copy()
    _flash_messages = []
    
    if category_filter:
        messages = [msg for msg in messages if msg["category"] in category_filter]
    
    if with_categories:
        return [(msg["category"], msg["message"]) for msg in messages]
    return [msg["message"] for msg in messages]

# 添加session支持
import secrets
import json
from typing import Dict, Any, Optional
from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import Response

# 创建上下文变量来存储当前会话
_session_ctx_var: ContextVar[Optional[Dict[str, Any]]] = ContextVar('session', default=None)
# 创建上下文变量来存储会话ID
_session_id_ctx_var: ContextVar[Optional[str]] = ContextVar('session_id', default=None)

class Session:
    """Flask风格的会话管理"""
    def __init__(self):
        self._data = _session_ctx_var.get()
        if self._data is None:
            self._data = {}
            _session_ctx_var.set(self._data)
        # 初始化会话属性
        self._permanent = False
        self._modified = False
    
    @property
    def config(self):
        """获取应用配置"""
        try:
            from .app import current_app
            return current_app.config
        except RuntimeError:
            # 在应用上下文之外，返回默认配置
            return {"PERMANENT_SESSION_LIFETIME": 31536000}
    
    @property
    def data(self) -> Dict[str, Any]:
        return self._data
    
    @property
    def permanent(self) -> bool:
        """会话是否永久"""
        return self._permanent
    
    @permanent.setter
    def permanent(self, value: bool) -> None:
        self._permanent = value
    
    @property
    def modified(self) -> bool:
        """会话是否被修改"""
        return self._modified
    
    @modified.setter
    def modified(self, value: bool) -> None:
        self._modified = value
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._modified = True
    
    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self._modified = True
    
    def __contains__(self, key: str) -> bool:
        return key in self._data
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取会话值"""
        return self._data.get(key, default)
    
    def pop(self, key: str, default: Any = None) -> Any:
        """移除并返回会话值"""
        value = self._data.pop(key, default)
        if key in self._data:
            self._modified = True
        return value
    
    def clear(self) -> None:
        """清空会话"""
        self._data.clear()
        self._modified = True
    
    def keys(self):
        """返回所有键"""
        return self._data.keys()
    
    def values(self):
        """返回所有值"""
        return self._data.values()
    
    def items(self):
        """返回所有键值对"""
        return self._data.items()
    
    def update(self, *args, **kwargs) -> None:
        """更新会话数据"""
        self._data.update(*args, **kwargs)
        self._modified = True
    
    def setdefault(self, key: str, default: Any = None) -> Any:
        """设置默认值"""
        if key not in self._data:
            self._modified = True
        return self._data.setdefault(key, default)

# 创建全局会话对象实例
_session_instance = Session()

def session() -> Session:
    """获取session对象"""
    return _session_instance

def get_session_id(request: Request) -> Optional[str]:
    """从请求中获取会话ID"""
    return request.cookies.get('session_id')

def set_session_cookie(response: Response, session_id: str, data: Dict[str, Any]) -> None:
    """设置会话cookie"""
    # 获取会话对象，检查是否为永久会话
    session_obj = session()
    
    # 根据会话是否永久设置过期时间
    if session_obj.permanent:
        # 永久会话，使用配置中的过期时间
        max_age = session_obj.config.get('PERMANENT_SESSION_LIFETIME', 31536000)  # 默认1年
    else:
        # 临时会话，使用默认过期时间
        max_age = 3600  # 1小时
    
    response.set_cookie(
        key='session_id',
        value=session_id,
        max_age=max_age,
        path='/',
        httponly=True,
        secure=False,  # 在生产环境中应该设置为True
        samesite='lax'
    )

def generate_session_id() -> str:
    """生成会话ID"""
    return secrets.token_hex(16)

def safe_join(directory: str, *pathnames: str) -> str:
    """安全地拼接路径"""
    from os.path import normpath, join, isabs
    from pathlib import Path
    
    # 确保目录是绝对路径
    if not isabs(directory):
        directory = str(Path(directory).absolute())
    
    # 拼接路径
    path = normpath(join(directory, *pathnames))
    
    # 检查路径是否在目录内
    if not path.startswith(directory):
        raise ValueError(f"Path {path} is not within directory {directory}")
    
    return path

def send_file(
    path_or_fileobj, 
    mimetype=None, 
    as_attachment=False, 
    download_name=None, 
    conditional=False,
    etag=True,
    last_modified=None,
    max_age=None,
    add_etags=True,
    etag_func=None
):
    """发送文件"""
    from starlette.responses import FileResponse
    from pathlib import Path
    
    # 处理文件路径
    if isinstance(path_or_fileobj, str):
        path = Path(path_or_fileobj)
    else:
        # 处理文件对象（简化实现）
        from io import BytesIO
        content = path_or_fileobj.read()
        from starlette.responses import Response
        return Response(content=content, media_type=mimetype or "application/octet-stream")
    
    # 检查文件是否存在
    if not path.exists() or not path.is_file():
        from .response import abort
        abort(404)
    
    # 创建文件响应
    return FileResponse(
        path=path,
        media_type=mimetype,
        filename=download_name,
        stat_result=None,
        method=None
    )

def url_quote(s, charset='utf-8', safe='/', encoding=None):
    """URL编码"""
    from urllib.parse import quote
    if isinstance(s, str):
        s = s.encode(charset)
    return quote(s, safe=safe)

def url_unquote(s, charset='utf-8', errors='replace'):
    """URL解码"""
    from urllib.parse import unquote
    if isinstance(s, bytes):
        s = s.decode(charset, errors)
    return unquote(s, encoding=charset, errors=errors)

def escape(s):
    """转义字符串"""
    from html import escape
    return escape(s)
