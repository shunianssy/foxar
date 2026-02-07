# 测试导入和基本功能
import sys

print("Starting test...")
print(f"Python version: {sys.version}")
print(f"Current directory: {sys.path[0]}")

# 尝试导入Foxar
try:
    from foxar import Foxar
    print("✓ Foxar imported successfully")
    
    # 尝试创建实例
    app = Foxar(__name__)
    print("✓ Foxar instance created successfully")
    
    # 尝试注册路由
    @app.route('/')
    def index():
        return 'Hello'
    print("✓ Route registered successfully")
    
    print("\nAll tests passed!")
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
