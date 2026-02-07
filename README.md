# foxar

A 100% Flask-compatible library built on top of FastAPI, providing the best of both worlds: Flask's simplicity and FastAPI's performance.

## Features

一个兼容Flask语法的FastAPI高性能库，结合了Flask的简洁语法和FastAPI的高性能特性。

## 特性

- **Flask兼容语法**：支持Flask的路由装饰器、蓝图系统和应用结构
- **FastAPI高性能**：底层使用FastAPI，支持异步处理和类型提示
- **自动API文档**：集成Swagger UI和ReDoc，自动生成API文档
- **类型安全**：支持Pydantic模型和类型提示
- **易于迁移**：允许现有Flask应用轻松迁移到高性能的FastAPI

## 安装

```bash
pip install foxar
```

## 基本使用

```python
from foxar import Foxar, jsonify

app = Foxar(__name__)

@app.route('/')
def index():
    return 'Hello, foxar!'

@app.route('/user/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id, 'message': f'Hello user {user_id}'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    return jsonify({'status': 'success', 'message': 'Login successful'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 蓝图使用

```python
from foxar import Foxar, Blueprint

app = Foxar(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/items')
def get_items():
    return {'items': ['item1', 'item2', 'item3']}

@api_bp.route('/items/<item_id>')
def get_item(item_id):
    return {'item_id': item_id, 'name': f'Item {item_id}'}

# 注册蓝图
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## 运行应用

### 使用内置run方法

```python
app.run(debug=True, port=5000)
```

### 使用uvicorn

```bash
uvicorn your_app:app --reload --port 5000
```

## 访问API文档

- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## 主要组件

1. **Foxar**：主应用类，继承自FastAPI，兼容Flask的初始化和路由语法
2. **Blueprint**：蓝图类，封装了FastAPI的APIRouter
3. **request**：请求对象，兼容Flask的request接口
4. **Response**：响应类，兼容Flask的Response接口
5. **jsonify**：JSON响应工具函数
6. **redirect**：重定向工具函数
7. **Config**：配置类，兼容Flask的Config接口
8. **url_for**：URL生成工具函数

## 注意事项

- 虽然兼容Flask的基本语法，但某些Flask特有功能可能需要额外实现
(当然，你如果实现了那就是太棒了！欢迎提交PR)
- 支持异步和同步路由处理函数
- 保持了FastAPI的所有高性能特性和类型提示
- 自动生成OpenAPI文档，提供交互式API测试界面

## 性能优势

- **异步支持**：底层使用FastAPI和Starlette，支持异步处理
- **类型提示**：利用Python类型提示提高代码质量
- **自动验证**：基于Pydantic的请求数据验证
- **高性能**：比传统WSGI框架（如Flask）具有更高的并发处理能力

foxar为开发者提供了一种既熟悉又高效的Web框架选择，让你可以使用Flask的简洁语法，同时享受FastAPI的高性能特性。


### Current Compatible Features
- Basic routing decorator `@app.route()`
- Blueprint support
- Request objects `request` and `g` object
- Response objects `Response` family
- Session management `session`
- Message flashing `flash`
- Error handling `errorhandler`
- Hook functions `before_request` and `after_request`
- Configuration management `Config`
- URL generation `url_for`
- Template rendering `render_template`
- Static file serving
- URL mapping `url_map` property

### Upcoming Features
- **Core Context Management**: `app_context()`, `request_context()`, `current_app` proxy
- **Session Management Enhancements**: Session persistence, `session.permanent`, `session.modified`
- **Error Handling Improvements**: `abort()` function, enhanced error handling
- **Routing System Enhancements**: Route aliases, route redirects, HTTP method support
- **Request Object Improvements**: `request.is_json`, `request.endpoint`, `request.view_args`
- **Response Object Enhancements**: Additional `Response` methods, improved `make_response()`
- **Utility Functions**: `safe_join()`, `send_file()`, `url_quote()`, `url_unquote()`, `escape()`
- **Configuration System Enhancements**: Environment variable support, configuration validation
- **Test Client Improvements**: Fully compatible Flask test client API
- **Signal System Improvements**: More Flask standard signals
- **Command Line Interface**: Flask CLI compatible interface
- **Blueprint System Enhancements**: Blueprint nesting, blueprint-level decorators
- **Template System Enhancements**: Template filters, global variables, context processors
- **Static File Service Enhancements**: Cache control, file compression
- **Security Features**: CSRF protection, XSS protection, CORS support
- **Other Flask Features**: `app.debug`, `app.testing`, enhanced message flashing, `g` object methods

## Quick Start

```python
from foxar import Foxar

app = Foxar(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()
```

## Installation

```bash
pip install foxar
```

## Why foxar?

1. **100% Flask Compatible**: Write Flask code and run it on FastAPI
2. **Performance**: Leverage FastAPI's asynchronous capabilities and automatic OpenAPI documentation
3. **Modern Python**: Take advantage of FastAPI's type hints and modern Python features
4. **Easy Migration**: Migrate existing Flask applications with minimal changes
5. **Extensible**: Use all FastAPI features alongside Flask-compatible code

## Documentation

For more information, please refer to the [documentation](docs/).

## Contributing

Contributions are welcome! Please see the [contributing guidelines](CONTRIBUTING.md) for more information.

## License

foxar is licensed under the AGPLv3 License. See the [LICENSE](LICENSE) file for details.
