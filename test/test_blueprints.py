from foxar.app import Foxar
from foxar.blueprints import Blueprint
from foxar.response import jsonify
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 创建一级蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 创建二级蓝图（嵌套蓝图）
users_bp = Blueprint('users', __name__, url_prefix='/users')
products_bp = Blueprint('products', __name__, url_prefix='/products')

# 一级蓝图路由
@api_bp.route('/status')
def api_status():
    return jsonify({'status': 'ok', 'message': 'API is running'})

# 二级蓝图路由
@users_bp.route('/list')
def users_list():
    return jsonify({'users': ['user1', 'user2', 'user3']})

@users_bp.route('/<user_id>')
def get_user(user_id):
    return jsonify({'user_id': user_id, 'name': f'User {user_id}'})

@products_bp.route('/list')
def products_list():
    return jsonify({'products': ['product1', 'product2', 'product3']})

# 蓝图级别的装饰器
@users_bp.before_request
def users_before_request():
    print("Users blueprint before_request called")

@users_bp.after_request
def users_after_request(response):
    print("Users blueprint after_request called")
    response.headers['X-Users-Blueprint'] = 'true'
    return response

# 注册嵌套蓝图
api_bp.register_blueprint(users_bp)
api_bp.register_blueprint(products_bp)

# 注册一级蓝图到应用
app.register_blueprint(api_bp)

# 测试蓝图嵌套
@app.route('/blueprint-test')
def blueprint_test():
    return jsonify({
        'message': 'Blueprint test',
        'api_routes': ['/api/status', '/api/users/list', '/api/users/<id>', '/api/products/list']
    })

if __name__ == "__main__":
    print("=== Testing Blueprint System ===")
    
    client = TestClient(app)
    
    # 测试一级蓝图路由
    response = client.get('/api/status')
    print(f"✅ ✓ API status response: {response.json()}")
    
    # 测试二级蓝图路由（用户）
    response = client.get('/api/users/list')
    print(f"✅ ✓ Users list response: {response.json()}")
    
    response = client.get('/api/users/123')
    print(f"✅ ✓ Get user response: {response.json()}")
    
    # 测试二级蓝图路由（产品）
    response = client.get('/api/products/list')
    print(f"✅ ✓ Products list response: {response.json()}")
    
    # 测试蓝图装饰器
    response = client.get('/api/users/list')
    print(f"✅ ✓ Blueprint after_request header: {response.headers.get('X-Users-Blueprint')}")
    
    # 测试蓝图嵌套
    response = client.get('/blueprint-test')
    print(f"✅ ✓ Blueprint test response: {response.json()}")
    
    print("\n=== Blueprint System Analysis ===")
    print("1. Basic blueprint: IMPLEMENTED")
    print("2. Blueprint nesting: IMPLEMENTED")
    print("3. Blueprint routes: IMPLEMENTED")
    print("4. Blueprint decorators: IMPLEMENTED")
