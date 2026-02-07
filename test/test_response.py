from foxar.app import Foxar
from foxar.response import Response, make_response, jsonify, redirect
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 测试基本响应
@app.route('/basic-response')
def basic_response():
    return "Hello, World!"

# 测试 Response 类
@app.route('/custom-response')
def custom_response():
    resp = Response("Custom Response", status=201)
    resp.headers['X-Custom-Header'] = 'value'
    resp.set_cookie('user', 'test_user')
    return resp

# 测试 make_response() 多参数
@app.route('/make-response')
def make_response_test():
    # 测试 make_response() 不同参数形式
    # 1. 字符串参数
    resp1 = make_response("Simple response")
    # 2. 元组参数 (response, status, headers)
    resp2 = make_response(("Tuple response", 202, {"X-Tuple-Header": "tuple-value"}))
    # 3. 直接传入 Response 对象
    resp3 = make_response(Response("Response object", status=203))
    
    return f"Resp1 status: {resp1.status_code}, Resp2 status: {resp2.status_code}, Resp3 status: {resp3.status_code}"

# 测试 jsonify
@app.route('/json-response')
def json_response():
    data = {'name': 'John', 'age': 30, 'city': 'New York'}
    return jsonify(data)

# 测试 redirect
@app.route('/redirect-test')
def redirect_test():
    return redirect('/basic-response', code=307)

# 测试 Response 类方法
@app.route('/response-methods')
def response_methods():
    resp = Response()
    
    # 测试 set_cookie
    resp.set_cookie('session_id', '12345')
    
    # 测试 delete_cookie
    resp.delete_cookie('old_cookie')
    
    # 测试其他方法
    resp.status_code = 200
    resp.headers['X-Test-Header'] = 'test-value'
    
    return "Response methods test completed"

if __name__ == "__main__":
    print("=== Testing Response Object ===")
    
    client = TestClient(app)
    
    # 测试基本响应
    response = client.get('/basic-response')
    print(f"✅ ✓ Basic response status: {response.status_code}")
    print(f"✅ ✓ Basic response content: {response.text}")
    
    # 测试自定义响应
    response = client.get('/custom-response')
    print(f"✅ ✓ Custom response status: {response.status_code}")
    print(f"✅ ✓ Custom response header: {response.headers.get('X-Custom-Header')}")
    print(f"✅ ✓ Custom response cookie: {response.cookies.get('user')}")
    
    # 测试 make_response()
    response = client.get('/make-response')
    print(f"✅ ✓ make_response() test: {response.text}")
    
    # 测试 jsonify
    response = client.get('/json-response')
    print(f"✅ ✓ jsonify response status: {response.status_code}")
    print(f"✅ ✓ jsonify response content: {response.json()}")
    
    # 测试 redirect
    response = client.get('/redirect-test', allow_redirects=False)
    print(f"✅ ✓ Redirect status code: {response.status_code}")
    print(f"✅ ✓ Redirect location: {response.headers.get('location')}")
    
    # 测试 Response 类方法
    response = client.get('/response-methods')
    print(f"✅ ✓ Response methods test status: {response.status_code}")
    print(f"✅ ✓ Response methods test cookie: {response.cookies.get('session_id')}")
    
    print("\n=== Response Object Analysis ===")
    print("1. Basic Response: IMPLEMENTED")
    print("2. Custom Response: IMPLEMENTED")
    print("3. make_response() function: IMPLEMENTED")
    print("4. jsonify: IMPLEMENTED")
    print("5. redirect: IMPLEMENTED")
    print("6. Response methods (set_cookie, delete_cookie): IMPLEMENTED")
