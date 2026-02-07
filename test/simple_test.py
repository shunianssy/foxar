try:
    from foxar import Foxar, Blueprint
    print("✓ Successfully imported Foxar and Blueprint")
    
    # 测试应用初始化
    app = Foxar(__name__)
    print("✓ Foxar initialized successfully")
    
    # 测试路由注册
    @app.route('/test')
    def test_route():
        return 'Test passed'
    print("✓ Route registered successfully")
    
    # 测试蓝图
    bp = Blueprint('test', __name__)
    @bp.route('/bp-test')
    def bp_test():
        return 'Blueprint test passed'
    app.register_blueprint(bp)
    print("✓ Blueprint registered successfully")
    
    print("\n🎉 All tests passed! foxar is working correctly.")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
