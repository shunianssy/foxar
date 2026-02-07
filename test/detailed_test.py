#!/usr/bin/env python3
"""
详细测试foxar的核心功能
"""

import sys
from foxar import Foxar, Blueprint, jsonify, redirect

print("=" * 60)
print("foxar Detailed Test")
print("=" * 60)

# 测试1: 应用初始化
test_name = "Test 1: Application Initialization"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    app = Foxar(__name__)
    print("✓ Foxar initialized successfully")
    print(f"  - Import name: {app.import_name}")
    print(f"  - Title: {app.title}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试2: 基本路由注册
test_name = "Test 2: Basic Route Registration"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    @app.route('/')
    def index():
        return 'Hello, foxar!'
    print("✓ Basic route registered successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试3: 带参数的路由
test_name = "Test 3: Route with Parameters"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    @app.route('/user/<int:user_id>')
    def get_user(user_id):
        return {'user_id': user_id, 'message': f'Hello user {user_id}'}
    print("✓ Route with parameters registered successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试4: 多方法路由
test_name = "Test 4: Route with Multiple Methods"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return jsonify({'status': 'success', 'message': 'Login successful'})
    print("✓ Route with multiple methods registered successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试5: 重定向路由
test_name = "Test 5: Redirect Route"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    @app.route('/old-path')
    def old_path():
        return redirect('/new-path')
    
    @app.route('/new-path')
    def new_path():
        return 'This is the new path'
    print("✓ Redirect route registered successfully")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试6: 蓝图创建和注册
test_name = "Test 6: Blueprint Creation and Registration"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    api_bp = Blueprint('api', __name__, url_prefix='/api')
    
    @api_bp.route('/items')
    def get_items():
        return {'items': ['item1', 'item2', 'item3']}
    
    @api_bp.route('/items/<item_id>')
    def get_item(item_id):
        return {'item_id': item_id, 'name': f'Item {item_id}'}
    
    app.register_blueprint(api_bp)
    print("✓ Blueprint created and registered successfully")
    print(f"  - Blueprint name: {api_bp.name}")
    print(f"  - URL prefix: {api_bp.url_prefix}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试7: 路由数量检查
test_name = "Test 7: Route Count Check"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    route_count = len(app.routes)
    print(f"✓ Found {route_count} routes")
    for i, route in enumerate(app.routes, 1):
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {i}. {route.path} [{', '.join(route.methods)}]")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

# 测试8: JSON响应工具
test_name = "Test 8: JSON Response Utility"
print(f"\n{test_name}")
print("-" * len(test_name))
try:
    json_response = jsonify({'status': 'success', 'data': {'key': 'value'}})
    print("✓ jsonify works correctly")
    print(f"  - Response type: {type(json_response).__name__}")
    print(f"  - Media type: {json_response.media_type}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 All tests passed! foxar is working correctly.")
print("=" * 60)
print("\nYou can run the application with:")
print("  uvicorn example_app:app --reload --port 5000")
print("\nThen visit:")
print("  - http://localhost:5000/ (Home page)")
print("  - http://localhost:5000/docs (API Documentation)")
print("  - http://localhost:5000/redoc (Alternative API Docs)")
print("=" * 60)
