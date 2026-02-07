from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware import Middleware
from starlette.responses import Response as StarletteResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from typing import Optional, List, Dict, Any, Callable, Union, Collection, Awaitable
from .blueprints import Blueprint
from .request import request_proxy, request_context

class HookMiddleware(BaseHTTPMiddleware):
    """处理Flask风格的钩子函数"""
    def __init__(self, app, app_instance):
        super().__init__(app)
        self.app_instance = app_instance
    
    async def dispatch(self, request: Request, call_next):
        # 设置请求上下文
        async with request_context(request):
            # 处理会话
            from .utils import get_session_id, generate_session_id, _session_ctx_var, _session_id_ctx_var
            
            # 获取或生成会话ID
            session_id = get_session_id(request)
            if not session_id:
                session_id = generate_session_id()
            
            # 设置会话ID上下文
            _session_id_ctx_var.set(session_id)
            # 初始化会话数据
            _session_ctx_var.set({})
            
            # 发送请求开始信号
            from .signals import request_started
            request_started.send(self.app_instance, request=request)
            
            try:
                # 执行请求前钩子
                for func in self.app_instance.before_request_funcs:
                    import inspect
                    if inspect.iscoroutinefunction(func):
                        result = await func()
                    else:
                        from starlette.concurrency import run_in_threadpool
                        result = await run_in_threadpool(func)
                    # 如果钩子返回响应，则直接返回
                    if result is not None:
                        # 保存会话数据到cookie
                        from .utils import set_session_cookie, session
                        session_data = session().data
                        set_session_cookie(result, session_id, session_data)
                        
                        # 发送请求结束信号
                        from .signals import request_finished
                        request_finished.send(self.app_instance, response=result)
                        
                        # 发送请求拆卸信号
                        from .signals import teardown_request
                        teardown_request.send(self.app_instance, exception=None)
                        
                        return result
                
                # 执行请求处理
                response = await call_next(request)
                
                # 执行请求后钩子
                for func in self.app_instance.after_request_funcs:
                    import inspect
                    if inspect.iscoroutinefunction(func):
                        response = await func(response)
                    else:
                        from starlette.concurrency import run_in_threadpool
                        response = await run_in_threadpool(func, response)
                
                # 保存会话数据到cookie
                from .utils import set_session_cookie, session
                session_data = session().data
                set_session_cookie(response, session_id, session_data)
                
                # 发送请求结束信号
                from .signals import request_finished
                request_finished.send(self.app_instance, response=response)
                
                # 发送请求拆卸信号
                from .signals import teardown_request
                teardown_request.send(self.app_instance, exception=None)
                
                return response
            except Exception as e:
                # 发送请求异常信号
                from .signals import request_exception
                request_exception.send(self.app_instance, exception=e)
                
                # 发送请求拆卸信号（带异常）
                from .signals import teardown_request
                teardown_request.send(self.app_instance, exception=e)
                
                raise

# 全局应用上下文变量
from contextvars import ContextVar
_current_app: ContextVar[Optional['Foxar']] = ContextVar('current_app', default=None)

class _AppProxy:
    """应用代理对象"""
    @property
    def _get_current_object(self):
        app = _current_app.get()
        if app is None:
            raise RuntimeError('在应用上下文之外访问 current_app')
        return app
    
    def __getattr__(self, name):
        return getattr(self._get_current_object, name)
    
    def __setattr__(self, name, value):
        setattr(self._get_current_object, name, value)
    
    def __delattr__(self, name):
        delattr(self._get_current_object, name)
    
    def __call__(self, *args, **kwargs):
        return self._get_current_object(*args, **kwargs)

# 创建全局应用代理对象
current_app = _AppProxy()

class _AppContext:
    """应用上下文管理器"""
    def __init__(self, app):
        self.app = app
        self.token = None
    
    def __enter__(self):
        # 设置应用上下文
        self.token = _current_app.set(self.app)
        # 发送应用上下文推送信号
        from .signals import appcontext_pushed
        appcontext_pushed.send(self.app)
        return self.app
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 发送应用上下文弹出信号
        from .signals import appcontext_popped
        appcontext_popped.send(self.app)
        
        # 发送应用上下文拆卸信号
        from .signals import teardown_appcontext
        teardown_appcontext.send(self.app, exception=exc_val)
        
        # 重置应用上下文
        if self.token:
            _current_app.reset(self.token)

class Foxar(FastAPI):
    def __init__(
        self,
        import_name: str,
        static_folder: Optional[str] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        instance_path: Optional[str] = None,
        instance_relative_config: bool = False,
        root_path: str = "",
        **kwargs
    ):
        super().__init__(
            title=import_name,
            root_path=root_path,
            **kwargs
        )
        self.import_name = import_name
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.template_folder = template_folder
        self.instance_path = instance_path
        self.instance_relative_config = instance_relative_config
        self.blueprints: List[Blueprint] = []
        
        # 初始化钩子函数列表
        self.before_request_funcs: List[Callable] = []
        self.after_request_funcs: List[Callable] = []
        
        # 初始化配置
        from .utils import Config
        self.config = Config(root_path=root_path)
        # 验证配置
        self.config.validate()
        
        # 注册钩子中间件
        self.add_middleware(HookMiddleware, app_instance=self)
        
        # 添加静态文件服务
        if static_folder is not None:
            from fastapi.staticfiles import StaticFiles
            static_url = static_url_path or "/static"
            
            # 创建静态文件服务，支持缓存控制
            static_files = StaticFiles(
                directory=static_folder,
                check_dir=True
            )
            
            # 挂载静态文件服务
            self.mount(static_url, static_files, name="static")
            
            # 存储静态文件配置
            self.static_files = static_files
        
        # 初始化模板引擎
        self.templates = None
        if template_folder is not None:
            from fastapi.templating import Jinja2Templates
            self.templates = Jinja2Templates(directory=template_folder)
    
    def app_context(self):
        """创建应用上下文"""
        return _AppContext(self)
    
    def route(
        self,
        rule: str,
        methods: Optional[Collection[str]] = None,
        endpoint: Optional[Callable] = None,
        provide_automatic_options: Optional[bool] = None,
        **options
    ):
        if methods is None:
            methods = ["GET"]
        
        def decorator(f: Callable) -> Callable:
            nonlocal endpoint
            if endpoint is None:
                endpoint = f
            
            # Flask风格的路由参数处理
            for opt_name, opt_value in options.items():
                if opt_name == "strict_slashes":
                    # FastAPI默认处理斜杠重定向
                    pass
                elif opt_name == "redirect_to":
                    # 处理重定向
                    async def redirect_handler(*args, **kwargs):
                        from starlette.responses import RedirectResponse
                        return RedirectResponse(url=opt_value)
                    endpoint = redirect_handler
            
            # 注册路由
            self.add_api_route(
                path=rule,
                endpoint=self._wrap_endpoint(endpoint),
                methods=list(methods),
                **options
            )
            return endpoint
        
        return decorator
    
    def _wrap_endpoint(self, endpoint: Callable) -> Callable:
        async def wrapped_endpoint(request: Request, *args, **kwargs):
            # 设置请求上下文
            async with request_context(request):
                return await self._run_endpoint(endpoint, *args, **kwargs)
        return wrapped_endpoint
    
    async def _run_endpoint(self, endpoint: Callable, *args, **kwargs):
        if hasattr(endpoint, "__wrapped__"):
            endpoint = endpoint.__wrapped__
        
        # 检查是否是异步函数
        import inspect
        if inspect.iscoroutinefunction(endpoint):
            return await endpoint(*args, **kwargs)
        else:
            # 同步函数在线程池中运行
            from starlette.concurrency import run_in_threadpool
            return await run_in_threadpool(endpoint, *args, **kwargs)
    
    def register_blueprint(
        self,
        blueprint: Blueprint,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        **options
    ):
        self.blueprints.append(blueprint)
        
        # 计算实际的URL前缀
        blueprint_prefix = url_prefix or blueprint.url_prefix or ""
        
        # 注册蓝图的路由
        self.include_router(
            router=blueprint.router,
            prefix=blueprint_prefix,
            **options
        )
        
        # 注册蓝图的嵌套蓝图
        for nested_blueprint in blueprint.blueprints:
            nested_prefix = nested_blueprint.url_prefix or ""
            full_prefix = blueprint_prefix
            if nested_prefix:
                if not full_prefix.endswith("/"):
                    full_prefix += "/"
                full_prefix += nested_prefix.lstrip("/")
            
            self.include_router(
                router=nested_blueprint.router,
                prefix=full_prefix,
                **options
            )
        
        # 执行蓝图的注册函数
        blueprint.register(self, options)
    
    def run(
        self,
        host: str = "127.0.0.1",
        port: int = 5000,
        debug: bool = False,
        load_dotenv: bool = True,
        **options
    ):
        import uvicorn
        
        if load_dotenv:
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass
        
        # 检查是否在主模块中运行
        import __main__
        app_import_str = None
        if hasattr(__main__, '__file__'):
            import os
            module_name = os.path.splitext(os.path.basename(__main__.__file__))[0]
            app_import_str = f"{module_name}:app"
        
        # 如果可以确定导入字符串，则使用它
        if app_import_str and debug:
            uvicorn.run(
                app_import_str,
                host=host,
                port=port,
                reload=debug,
                **options
            )
        else:
            # 否则直接传递app对象（不启用reload）
            uvicorn.run(
                app=self,
                host=host,
                port=port,
                reload=False,  # 禁用reload以避免警告
                **options
            )
    
    def add_url_rule(
        self,
        rule: str,
        endpoint: Optional[str] = None,
        view_func: Optional[Callable] = None,
        methods: Optional[List[str]] = None,
        provide_automatic_options: Optional[bool] = None,
        **options
    ):
        if methods is None:
            methods = ["GET"]
        
        if view_func is not None:
            self.add_api_route(
                path=rule,
                endpoint=self._wrap_endpoint(view_func),
                methods=methods,
                name=endpoint,
                **options
            )
    
    def before_request(self, f: Callable) -> Callable:
        """注册请求前钩子"""
        self.before_request_funcs.append(f)
        return f
    
    def after_request(self, f: Callable) -> Callable:
        """注册请求后钩子"""
        self.after_request_funcs.append(f)
        return f
    
    def errorhandler(self, code_or_exception: Union[int, type]) -> Callable:
        """注册错误处理函数"""
        def decorator(f: Callable) -> Callable:
            # 这里可以注册错误处理
            # FastAPI使用异常处理机制
            if isinstance(code_or_exception, int):
                # 注册HTTP错误码处理
                @self.exception_handler(code_or_exception)
                async def http_error_handler(request: Request, exc):
                    import inspect
                    # 检查函数签名，支持不同的参数形式
                    sig = inspect.signature(f)
                    try:
                        if len(sig.parameters) == 2:
                            # 支持 (request, exc) 形式
                            if inspect.iscoroutinefunction(f):
                                return await f(request, exc)
                            else:
                                from starlette.concurrency import run_in_threadpool
                                return await run_in_threadpool(f, request, exc)
                        else:
                            # 支持 (exc) 形式
                            if inspect.iscoroutinefunction(f):
                                return await f(exc)
                            else:
                                from starlette.concurrency import run_in_threadpool
                                return await run_in_threadpool(f, exc)
                    except Exception as e:
                        # 如果错误处理函数本身出错，返回500错误
                        from starlette.responses import PlainTextResponse
                        return PlainTextResponse(str(e), status_code=500)
            else:
                # 注册异常类型处理
                @self.exception_handler(code_or_exception)
                async def exception_handler(request: Request, exc):
                    import inspect
                    # 检查函数签名，支持不同的参数形式
                    sig = inspect.signature(f)
                    try:
                        if len(sig.parameters) == 2:
                            # 支持 (request, exc) 形式
                            if inspect.iscoroutinefunction(f):
                                return await f(request, exc)
                            else:
                                from starlette.concurrency import run_in_threadpool
                                return await run_in_threadpool(f, request, exc)
                        else:
                            # 支持 (exc) 形式
                            if inspect.iscoroutinefunction(f):
                                return await f(exc)
                            else:
                                from starlette.concurrency import run_in_threadpool
                                return await run_in_threadpool(f, exc)
                    except Exception as e:
                        # 如果错误处理函数本身出错，返回500错误
                        from starlette.responses import PlainTextResponse
                        return PlainTextResponse(str(e), status_code=500)
            return f
        return decorator
    
    def register_error_handler(self, code_or_exception: Union[int, type], f: Callable) -> Callable:
        """注册错误处理函数（与errorhandler装饰器功能相同）"""
        return self.errorhandler(code_or_exception)(f)
    
    def handle_exception(self, e: Exception) -> Any:
        """处理异常"""
        # 这里可以添加全局异常处理逻辑
        raise e
    
    @property
    def url_map(self):
        """返回URL映射"""
        # 构建URL映射
        url_map = {}
        
        # 遍历所有路由
        for route in self.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                # 获取路由路径和方法
                path = route.path
                methods = route.methods if hasattr(route, 'methods') else {'GET'}
                endpoint = route.name if hasattr(route, 'name') else None
                
                # 构建路由信息
                route_info = {
                    'path': path,
                    'methods': methods,
                    'endpoint': endpoint
                }
                
                # 添加到URL映射
                if path not in url_map:
                    url_map[path] = []
                url_map[path].append(route_info)
        
        # 遍历蓝图的路由（包括嵌套蓝图）
        def process_blueprint(blueprint, parent_path=""):
            for route in blueprint.router.routes:
                if hasattr(route, 'path') and hasattr(route, 'methods'):
                    # 获取路由路径和方法
                    path = route.path
                    methods = route.methods if hasattr(route, 'methods') else {'GET'}
                    endpoint = route.name if hasattr(route, 'name') else None
                    
                    # 构建路由信息
                    route_info = {
                        'path': path,
                        'methods': methods,
                        'endpoint': endpoint,
                        'blueprint': blueprint.name
                    }
                    
                    # 添加到URL映射
                    if path not in url_map:
                        url_map[path] = []
                    url_map[path].append(route_info)
            
            # 递归处理嵌套蓝图
            for nested_blueprint in blueprint.blueprints:
                process_blueprint(nested_blueprint, parent_path + (blueprint.url_prefix or ""))
        
        # 处理所有直接注册的蓝图
        for blueprint in self.blueprints:
            process_blueprint(blueprint)
        
        return url_map
    
    def url_for(self, endpoint: str, **values) -> str:
        """生成URL"""
        from .utils import url_for
        return url_for(endpoint, **values)
    
    def render_template(self, template_name: str, **context) -> HTMLResponse:
        """渲染模板"""
        if self.templates is None:
            raise RuntimeError("Template folder not set")
        
        # 获取当前请求对象
        from .request import request, g
        req = request.request
        
        # 构建上下文
        template_context = {**context, "request": request, "g": g}
        
        # 发送模板渲染前信号
        from .signals import before_render_template
        before_render_template.send(self, template=template_name, context=template_context)
        
        # 发送模板渲染信号
        from .signals import template_rendered
        template_rendered.send(self, template=template_name, context=template_context)
        
        # 渲染模板
        return self.templates.TemplateResponse(
            name=template_name,
            context=template_context,
            request=req
        )
    
    def use(self, middleware) -> None:
        """注册中间件（Flask风格）"""
        # 对于Flask风格的中间件，我们需要适配到Starlette中间件
        # 这里提供一个简化的实现
        self.add_middleware(middleware)
    
    def send_from_directory(self, directory, path, **options):
        """从目录发送文件"""
        from starlette.responses import FileResponse
        from pathlib import Path
        
        # 构建文件路径
        file_path = Path(directory) / path
        
        # 检查文件是否存在
        if not file_path.exists() or not file_path.is_file():
            from starlette.responses import Response
            return Response("File not found", status_code=404)
        
        # 获取缓存控制选项
        mimetype = options.get('mimetype')
        as_attachment = options.get('as_attachment', False)
        filename = options.get('filename')
        
        # 创建文件响应
        return FileResponse(
            path=file_path,
            media_type=mimetype,
            filename=filename,
            stat_result=None,
            method=None
        )
    
    def static_url_path_for(self, filename, **values):
        """生成静态文件URL"""
        from .utils import url_for
        return url_for('static', filename=filename, **values)
    
    @property
    def wsgi_app(self):
        """WSGI应用（兼容Flask）"""
        # 这里可以返回一个WSGI包装器
        return self
    
    @property
    def asgi_app(self):
        """ASGI应用"""
        return self
