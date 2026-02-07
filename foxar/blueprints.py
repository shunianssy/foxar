from fastapi import APIRouter
from typing import Optional, List, Dict, Any, Callable, Collection, Union

class Blueprint:
    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: Optional[str] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        url_defaults: Optional[Dict[str, Any]] = None,
        root_path: str = ""
    ):
        self.name = name
        self.import_name = import_name
        self.static_folder = static_folder
        self.static_url_path = static_url_path
        self.template_folder = template_folder
        self.url_prefix = url_prefix
        self.subdomain = subdomain
        self.url_defaults = url_defaults or {}
        self.root_path = root_path
        
        # 初始化 APIRouter
        self.router = APIRouter(
            prefix=url_prefix or "",
            **{k: v for k, v in locals().items() if k in ['tags', 'dependencies', 'responses']}
        )
        
        self.deferred_functions: List[Callable] = []
        self.blueprints: List[Blueprint] = []
    
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
            
            # 注册路由到 APIRouter
            self.router.add_api_route(
                path=rule,
                endpoint=endpoint,
                methods=list(methods),
                **options
            )
            return endpoint
        
        return decorator
    
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
            self.router.add_api_route(
                path=rule,
                endpoint=view_func,
                methods=methods,
                name=endpoint,
                **options
            )
    
    def before_request(self, f: Callable) -> Callable:
        # 实现请求前钩子
        self.deferred_functions.append(lambda app: app.before_request(f))
        return f
    
    def after_request(self, f: Callable) -> Callable:
        # 实现请求后钩子
        self.deferred_functions.append(lambda app: app.after_request(f))
        return f
    
    def errorhandler(self, code_or_exception: Union[int, type]) -> Callable:
        # 实现错误处理
        def decorator(f: Callable) -> Callable:
            self.deferred_functions.append(lambda app: app.errorhandler(code_or_exception)(f))
            return f
        return decorator
    
    def register_blueprint(
        self,
        blueprint: 'Blueprint',
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        **options
    ):
        """注册蓝图到当前蓝图（支持嵌套蓝图）"""
        self.blueprints.append(blueprint)
        
        # 计算实际的URL前缀
        actual_prefix = self.url_prefix or ""
        blueprint_prefix = url_prefix or blueprint.url_prefix or ""
        if blueprint_prefix and not blueprint_prefix.startswith("/"):
            blueprint_prefix = "/" + blueprint_prefix
        if actual_prefix and not actual_prefix.endswith("/"):
            actual_prefix = actual_prefix + "/"
        full_prefix = actual_prefix + blueprint_prefix.lstrip("/")
        
        # 更新蓝图的APIRouter前缀
        blueprint.router.prefix = full_prefix
        
        # 注册蓝图的路由到当前蓝图的路由器
        for route in blueprint.router.routes:
            self.router.routes.append(route)
        
        # 注册嵌套蓝图的延迟函数
        for deferred in blueprint.deferred_functions:
            self.deferred_functions.append(deferred)
        
        # 递归注册嵌套蓝图
        for nested_blueprint in blueprint.blueprints:
            self.register_blueprint(nested_blueprint, **options)
    
    def register(self, app, options: Dict[str, Any] = None):
        # 注册蓝图到应用
        if options is None:
            options = {}
        
        # 执行延迟函数
        for deferred in self.deferred_functions:
            deferred(app)
        
        # 注册嵌套蓝图
        for blueprint in self.blueprints:
            blueprint.register(app, options)
