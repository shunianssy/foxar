import secrets
import hmac
import hashlib
from typing import Optional, Dict, Any
from contextvars import ContextVar
from starlette.requests import Request
from starlette.responses import Response

# 创建上下文变量来存储 CSRF 令牌
_csrf_token_ctx_var: ContextVar[Optional[str]] = ContextVar('csrf_token', default=None)

class CSRFProtect:
    """CSRF 保护类"""
    def __init__(self):
        self._exempt_views = set()
    
    def init_app(self, app):
        """初始化应用"""
        # 设置默认配置
        app.config.setdefault('WTF_CSRF_ENABLED', True)
        app.config.setdefault('WTF_CSRF_SECRET_KEY', app.config.get('SECRET_KEY'))
        app.config.setdefault('WTF_CSRF_METHODS', {'POST', 'PUT', 'PATCH', 'DELETE'})
        app.config.setdefault('WTF_CSRF_FIELD_NAME', 'csrf_token')
        app.config.setdefault('WTF_CSRF_HEADERS', ['X-CSRFToken', 'X-CSRF-Token'])
        app.config.setdefault('WTF_CSRF_TIME_LIMIT', 3600)  # 1小时
        
        # 添加 CSRF 保护中间件
        @app.middleware('http')
        async def csrf_protect_middleware(request: Request, call_next):
            if not app.config.get('WTF_CSRF_ENABLED'):
                return await call_next(request)
            
            # 检查是否为需要保护的方法
            if request.method in app.config.get('WTF_CSRF_METHODS', {'POST', 'PUT', 'PATCH', 'DELETE'}):
                # 验证 CSRF 令牌
                if not await self._validate_csrf(request, app):
                    from .response import abort
                    abort(400, 'CSRF token validation failed')
            
            # 生成 CSRF 令牌
            token = self.generate_csrf(app)
            _csrf_token_ctx_var.set(token)
            
            # 处理请求
            response = await call_next(request)
            
            # 设置 CSRF 令牌到 cookie
            self.set_csrf_cookie(response, app)
            
            return response
    
    def generate_csrf(self, app) -> str:
        """生成 CSRF 令牌"""
        secret_key = app.config.get('WTF_CSRF_SECRET_KEY') or app.config.get('SECRET_KEY')
        if not secret_key:
            raise RuntimeError('CSRF secret key not set')
        
        # 生成随机令牌
        token = secrets.token_hex(32)
        
        # 签名令牌
        h = hmac.new(secret_key.encode('utf-8'), token.encode('utf-8'), hashlib.sha256)
        signed_token = f"{token}.{h.hexdigest()}"
        
        return signed_token
    
    async def _validate_csrf(self, request: Request, app) -> bool:
        """验证 CSRF 令牌"""
        secret_key = app.config.get('WTF_CSRF_SECRET_KEY') or app.config.get('SECRET_KEY')
        if not secret_key:
            return True  # 没有密钥，跳过验证
        
        # 从请求中获取令牌
        token = await self._get_csrf_token(request, app)
        if not token:
            return False
        
        # 验证令牌
        try:
            token_part, hmac_part = token.split('.')
            h = hmac.new(secret_key.encode('utf-8'), token_part.encode('utf-8'), hashlib.sha256)
            return hmac.compare_digest(hmac_part, h.hexdigest())
        except ValueError:
            return False
    
    async def _get_csrf_token(self, request: Request, app) -> Optional[str]:
        """从请求中获取 CSRF 令牌"""
        field_name = app.config.get('WTF_CSRF_FIELD_NAME', 'csrf_token')
        headers = app.config.get('WTF_CSRF_HEADERS', ['X-CSRFToken', 'X-CSRF-Token'])
        
        # 从表单中获取
        try:
            form_data = await request.form()
            if field_name in form_data:
                return form_data[field_name]
        except Exception:
            pass
        
        # 从 JSON 中获取
        try:
            json_data = await request.json()
            if field_name in json_data:
                return json_data[field_name]
        except Exception:
            pass
        
        # 从头部中获取
        for header in headers:
            if header in request.headers:
                return request.headers[header]
        
        # 从 cookie 中获取
        return request.cookies.get(field_name)
    
    def set_csrf_cookie(self, response: Response, app) -> None:
        """设置 CSRF 令牌到 cookie"""
        if not app.config.get('WTF_CSRF_ENABLED'):
            return
        
        field_name = app.config.get('WTF_CSRF_FIELD_NAME', 'csrf_token')
        token = _csrf_token_ctx_var.get() or self.generate_csrf(app)
        
        response.set_cookie(
            key=field_name,
            value=token,
            max_age=app.config.get('WTF_CSRF_TIME_LIMIT', 3600),
            path=app.config.get('APPLICATION_ROOT', '/'),
            httponly=False,  # CSRF 令牌需要在前端访问
            secure=app.config.get('PREFERRED_URL_SCHEME') == 'https',
            samesite='lax'
        )
    
    def get_csrf_token(self, app) -> str:
        """获取 CSRF 令牌"""
        token = _csrf_token_ctx_var.get()
        if not token:
            token = self.generate_csrf(app)
            _csrf_token_ctx_var.set(token)
        return token
    
    def exempt(self, view_func):
        """豁免视图函数的 CSRF 保护"""
        self._exempt_views.add(view_func)
        return view_func

# 创建全局 CSRF 保护实例
csrf = CSRFProtect()

# 提供与 Flask-WTF 兼容的函数
def generate_csrf(app=None):
    """生成 CSRF 令牌"""
    if app is None:
        from .app import current_app
        app = current_app
    return csrf.generate_csrf(app)

def validate_csrf(token, app=None):
    """验证 CSRF 令牌"""
    if app is None:
        from .app import current_app
        app = current_app
    
    secret_key = app.config.get('WTF_CSRF_SECRET_KEY') or app.config.get('SECRET_KEY')
    if not secret_key:
        return True
    
    try:
        token_part, hmac_part = token.split('.')
        h = hmac.new(secret_key.encode('utf-8'), token_part.encode('utf-8'), hashlib.sha256)
        return hmac.compare_digest(hmac_part, h.hexdigest())
    except ValueError:
        return False
