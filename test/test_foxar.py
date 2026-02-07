from foxar import Foxar, request, jsonify, make_response, redirect, flash, get_flashed_messages, session, TestClient

# 创建应用实例
app = Foxar(__name__)

# 配置
app.config['SECRET_KEY'] = 'test-secret-key'

# 测试请求前钩子
@app.before_request
def before_request():
    print("Before request")

# 测试请求后钩子
@app.after_request
def after_request(response):
    print("After request")
    return response

# 测试错误处理
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found"}), 404

# 测试基本路由
@app.route('/')
def hello():
    return {'message': 'Hello World'}

# 测试带参数的路由
@app.route('/user/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id}

# 测试POST请求
@app.route('/login', methods=['POST'])
def login():
    # 测试请求对象
    username = request.args_get('username', '')
    password = request.args_get('password', '')
    return {'username': username, 'password': password}

# 测试响应对象
@app.route('/response')
def test_response():
    resp = make_response({'message': 'Custom response'})
    resp.set_cookie('test_cookie', 'test_value')
    return resp

# 测试重定向
@app.route('/redirect')
def test_redirect():
    return redirect('/')

# 测试flash消息
@app.route('/flash')
def test_flash():
    flash('This is a flash message')
    return {'message': 'Flash message added'}

# 测试获取flash消息
@app.route('/get_flashed')
def test_get_flashed():
    messages = get_flashed_messages()
    return {'messages': messages}

# 测试session
@app.route('/session')
def test_session():
    session_data = session()
    session_data['test'] = 'session_value'
    return {'session': session_data}

# 测试url_for
@app.route('/url_for')
def test_url_for():
    url = app.url_for('get_user', user_id=123)
    return {'url': url}

# 测试蓝图
from foxar import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/items')
def get_items():
    return {'items': ['item1', 'item2']}

app.register_blueprint(api_bp)

# 测试运行
if __name__ == '__main__':
    # 运行测试
    print("Testing foxar compatibility...")
    
    # 使用测试客户端
    client = TestClient(app)
    
    # 测试基本路由
    response = client.get('/')
    print(f"GET /: {response.status_code}, {response.json()}")
    
    # 测试带参数的路由
    response = client.get('/user/123')
    print(f"GET /user/123: {response.status_code}, {response.json()}")
    
    # 测试POST请求
    response = client.post('/login?username=test&password=123')
    print(f"POST /login: {response.status_code}, {response.json()}")
    
    # 测试响应对象
    response = client.get('/response')
    print(f"GET /response: {response.status_code}, {response.json()}")
    print(f"Cookies: {dict(response.cookies)}")
    
    # 测试重定向
    response = client.get('/redirect', follow_redirects=True)
    print(f"GET /redirect: {response.status_code}, {response.json()}")
    
    # 测试flash消息
    client.get('/flash')
    response = client.get('/get_flashed')
    print(f"GET /get_flashed: {response.status_code}, {response.json()}")
    
    # 测试session
    response = client.get('/session')
    print(f"GET /session: {response.status_code}, {response.json()}")
    
    # 测试url_for
    response = client.get('/url_for')
    print(f"GET /url_for: {response.status_code}, {response.json()}")
    
    # 测试蓝图
    response = client.get('/api/items')
    print(f"GET /api/items: {response.status_code}, {response.json()}")
    
    # 测试404错误
    response = client.get('/not_found')
    print(f"GET /not_found: {response.status_code}, {response.json()}")
    
    print("All tests completed!")
    
    # 启动开发服务器
    # app.run(debug=True)
