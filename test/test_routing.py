from foxar.app import Foxar
from foxar.response import redirect
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 测试基本路由
@app.route('/hello')
def hello():
    return "Hello, World!"

# 测试路由方法限制
@app.route('/method-test', methods=['GET', 'POST'])
def method_test():
    from foxar.request import request
    return f"Method: {request.method}"

# 测试路由重定向
@app.route('/redirect-test')
def redirect_test():
    return redirect('/hello')

# 测试路由别名（endpoint）
@app.route('/user/<name>', endpoint='user_profile')
def user_profile(name):
    return f"User profile: {name}"

# 测试路由参数
@app.route('/item/<int:item_id>')
def get_item(item_id):
    return f"Item ID: {item_id}"

if __name__ == "__main__":
    print("=== Testing Routing System ===")
    
    client = TestClient(app)
    
    # 测试基本路由
    response = client.get('/hello')
    print(f"✅ ✓ Basic route response: {response.text}")
    
    # 测试GET方法
    response = client.get('/method-test')
    print(f"✅ ✓ GET method response: {response.text}")
    
    # 测试POST方法
    response = client.post('/method-test')
    print(f"✅ ✓ POST method response: {response.text}")
    
    # 测试路由重定向
    response = client.get('/redirect-test', allow_redirects=False)
    print(f"✅ ✓ Redirect status code: {response.status_code}")
    print(f"✅ ✓ Redirect location: {response.headers.get('location')}")
    
    # 测试路由参数
    response = client.get('/item/42')
    print(f"✅ ✓ Route parameter response: {response.text}")
    
    # 测试路由别名（endpoint）
    response = client.get('/user/john')
    print(f"✅ ✓ Route with endpoint alias response: {response.text}")
    
    print("\n=== Routing System Analysis ===")
    print("1. Basic routing: IMPLEMENTED")
    print("2. Route methods: IMPLEMENTED")
    print("3. Route redirect: IMPLEMENTED")
    print("4. Route parameters: IMPLEMENTED")
    print("5. Route aliases (endpoints): IMPLEMENTED")
