from foxar.app import Foxar, current_app
from foxar.request import request_context
from starlette.requests import Request
from starlette.datastructures import Headers

# 创建应用实例
app = Foxar(__name__)

# 测试 app_context()
def test_app_context():
    print("Testing app_context()...")
    # 验证在上下文外访问 current_app 会抛出异常
    try:
        _ = current_app
        print("ERROR: current_app should raise exception outside context")
    except RuntimeError as e:
        print(f"✓ Correctly raised exception: {e}")
    
    # 测试在上下文中访问 current_app
    with app.app_context():
        assert current_app is app
        print("✓ current_app correctly points to app inside context")

# 测试 request_context()
async def test_request_context():
    print("\nTesting request_context()...")
    # 创建一个模拟请求
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": Headers({"host": "localhost:8000"}).raw,
    }
    
    async with request_context(Request(scope, receive=lambda: {"type": "http.request"})):
        from foxar.request import request
        assert request.method == "GET"
        assert request.path == "/test"
        print("✓ request object correctly populated inside request_context")

if __name__ == "__main__":
    test_app_context()
    import asyncio
    asyncio.run(test_request_context())
    print("\nAll context management tests completed!")
