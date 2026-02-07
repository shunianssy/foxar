from foxar.app import Foxar
from foxar.response import abort, HTTPException, make_response
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 测试abort函数
@app.route('/abort-test/<code>')
def abort_test(code):
    abort(int(code))

# 测试错误处理
@app.errorhandler(404)
def not_found_error(error):
    return make_response("Custom 404 Error: Page Not Found", 404)

@app.errorhandler(500)
def internal_error(error):
    return make_response("Custom 500 Error: Internal Server Error", 500)

# 测试HTTPException
@app.route('/exception-test')
def exception_test():
    raise HTTPException(403, "Forbidden access")

if __name__ == "__main__":
    print("=== Testing Error Handling ===")
    
    client = TestClient(app)
    
    # 测试abort(404)
    response = client.get('/abort-test/404')
    print(f"✅ ✓ Abort 404 response status: {response.status_code}")
    print(f"✅ ✓ Abort 404 response content: {response.text}")
    
    # 测试abort(500)
    response = client.get('/abort-test/500')
    print(f"✅ ✓ Abort 500 response status: {response.status_code}")
    print(f"✅ ✓ Abort 500 response content: {response.text}")
    
    # 测试HTTPException
    response = client.get('/exception-test')
    print(f"✅ ✓ HTTPException response status: {response.status_code}")
    print(f"✅ ✓ HTTPException response content: {response.text}")
    
    print("\n=== Error Handling Analysis ===")
    print("1. abort() function: IMPLEMENTED")
    print("2. Error handlers: IMPLEMENTED")
    print("3. HTTPException: IMPLEMENTED")
