# 极简测试脚本
print("Testing foxar...")
try:
    from foxar import Foxar
    print("✓ Successfully imported Foxar")
    
    app = Foxar(__name__)
    print("✓ Successfully created Foxar instance")
    
    @app.route('/test')
    def test():
        return 'Test'
    print("✓ Successfully registered route")
    
    print("\nAll tests passed! foxar is working correctly.")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
