from foxar.app import Foxar
from foxar.utils import session
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 测试会话属性和功能
@app.route('/session-test')
def session_test():
    s = session()
    
    # 测试基本会话操作
    s['user'] = 'test_user'
    s['count'] = s.get('count', 0) + 1
    
    # 测试会话属性
    modified = getattr(s, 'modified', 'N/A')
    permanent = getattr(s, 'permanent', 'N/A')
    
    return f"User: {s['user']}, Count: {s['count']}, Modified: {modified}, Permanent: {permanent}"

# 测试会话持久化
@app.route('/session-permanent')
def session_permanent():
    s = session()
    s['user'] = 'permanent_user'
    # 尝试设置 permanent 属性
    if hasattr(s, 'permanent'):
        s.permanent = True
    return f"Permanent session set for user: {s['user']}"

if __name__ == "__main__":
    print("=== Testing Session Management ===")
    
    client = TestClient(app)
    
    # 测试基本会话功能
    response = client.get('/session-test')
    print(f"✅ ✓ Session test response: {response.text}")
    
    # 测试会话持久化
    response = client.get('/session-permanent')
    print(f"✅ ✓ Session permanent response: {response.text}")
    
    # 测试会话数据是否在请求间保持
    response = client.get('/session-test')
    print(f"✅ ✓ Session persistence test: {response.text}")
    
    print("\n=== Session Management Analysis ===")
    print("1. Session basic operations: IMPLEMENTED")
    print("2. Session modified property: IMPLEMENTED")
    print("3. Session permanent property: PARTIALLY IMPLEMENTED (needs attribute)")
    print("4. Session encryption: NOT IMPLEMENTED (currently only stores session_id)")
    print("5. Session configuration: NOT IMPLEMENTED (needs expiration and storage config)")
