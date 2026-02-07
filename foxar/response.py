from starlette.responses import Response as StarletteResponse
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from typing import Optional, Dict, Any, Union

class Response(StarletteResponse):
    def __init__(
        self,
        response=None,
        status=200,
        headers=None,
        mimetype=None,
        content_type=None,
        direct_passthrough=False
    ):
        # 处理不同类型的响应
        if response is None:
            content = b''
        elif isinstance(response, (dict, list)):
            # 处理JSON数据
            from fastapi.encoders import jsonable_encoder
            content = jsonable_encoder(response)
            if content_type is None and mimetype is None:
                content_type = "application/json"
        elif isinstance(response, bytes):
            content = response
        else:
            content = str(response).encode('utf-8')
        
        # 处理头部
        if headers is None:
            headers = {}
        
        # 处理内容类型
        if content_type is None:
            if mimetype is not None:
                content_type = mimetype
            else:
                content_type = "text/html; charset=utf-8"
        
        super().__init__(
            content=content,
            status_code=status,
            headers=headers,
            media_type=content_type
        )
        self.direct_passthrough = direct_passthrough
    
    def set_cookie(
        self,
        key,
        value='',
        max_age=None,
        expires=None,
        path='/',
        domain=None,
        secure=False,
        httponly=False,
        samesite=None
    ):
        """设置cookie"""
        from starlette.datastructures import MutableHeaders
        
        # 使用Starlette的cookie设置机制
        cookie_headers = MutableHeaders()
        cookie_headers.set_cookie(
            key=key,
            value=value,
            max_age=max_age,
            expires=expires,
            path=path,
            domain=domain,
            secure=secure,
            httponly=httponly,
            samesite=samesite
        )
        
        # 将cookie添加到响应头部
        for name, value in cookie_headers.items():
            if name.lower() == 'set-cookie':
                if 'set-cookie' in self.headers:
                    self.headers.append('set-cookie', value)
                else:
                    self.headers['set-cookie'] = value
    
    def delete_cookie(
        self,
        key,
        path='/',
        domain=None
    ):
        """删除cookie"""
        self.set_cookie(
            key=key,
            value='',
            max_age=0,
            expires=0,
            path=path,
            domain=domain
        )

class JSONResponse(Response):
    def __init__(
        self,
        response=None,
        status=200,
        headers=None,
        mimetype=None,
        content_type=None,
        direct_passthrough=False
    ):
        if content_type is None and mimetype is None:
            content_type = "application/json"
        
        super().__init__(
            response=response,
            status=status,
            headers=headers,
            mimetype=mimetype,
            content_type=content_type,
            direct_passthrough=direct_passthrough
        )

class HTMLResponse(Response):
    def __init__(
        self,
        response=None,
        status=200,
        headers=None,
        mimetype=None,
        content_type=None,
        direct_passthrough=False
    ):
        if content_type is None and mimetype is None:
            content_type = "text/html; charset=utf-8"
        
        super().__init__(
            response=response,
            status=status,
            headers=headers,
            mimetype=mimetype,
            content_type=content_type,
            direct_passthrough=direct_passthrough
        )

class PlainTextResponse(Response):
    def __init__(
        self,
        response=None,
        status=200,
        headers=None,
        mimetype=None,
        content_type=None,
        direct_passthrough=False
    ):
        if content_type is None and mimetype is None:
            content_type = "text/plain; charset=utf-8"
        
        super().__init__(
            response=response,
            status=status,
            headers=headers,
            mimetype=mimetype,
            content_type=content_type,
            direct_passthrough=direct_passthrough
        )

def make_response(
    response=None,
    status=None,
    headers=None
) -> Response:
    """创建响应对象"""
    if isinstance(response, Response):
        if status is not None:
            response.status_code = status
        if headers is not None:
            response.headers.update(headers)
        return response
    return Response(response=response, status=status or 200, headers=headers)

def jsonify(*args, **kwargs) -> JSONResponse:
    """创建JSON响应"""
    if args and kwargs:
        raise TypeError("jsonify() can't mix args and kwargs")
    elif len(args) == 1:
        data = args[0]
    else:
        data = kwargs
    return JSONResponse(data)

# 提供与Flask兼容的响应函数
def redirect(location, code=302, Response=RedirectResponse):
    """创建重定向响应"""
    return Response(url=location, status_code=code)

class HTTPException(Exception):
    """HTTP异常类"""
    def __init__(self, code, description=None):
        self.code = code
        self.description = description
        super().__init__(self.description or f"HTTP Error {code}")

def abort(code, *args, **kwargs):
    """中断请求并返回指定的HTTP错误码"""
    raise HTTPException(code, *args, **kwargs)
