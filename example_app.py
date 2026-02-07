from foxar import Foxar, Blueprint, request, jsonify, redirect

# 创建主应用实例
app = Foxar(__name__)

# 基本路由示例
@app.route('/')
def index():
    return 'Hello, foxar!'

# 带参数的路由
@app.route('/user/<int:user_id>')
def get_user(user_id):
    return {'user_id': user_id, 'message': f'Hello user {user_id}'}

# 多方法路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 处理登录逻辑
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return 'Login page'

# 重定向示例
@app.route('/old-path')
def old_path():
    return redirect('/new-path')

@app.route('/new-path')
def new_path():
    return 'This is the new path'

# 蓝图示例
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/items')
def get_items():
    return {'items': ['item1', 'item2', 'item3']}

@api_bp.route('/items/<item_id>')
def get_item(item_id):
    return {'item_id': item_id, 'name': f'Item {item_id}'}

# 注册蓝图
app.register_blueprint(api_bp)

# 运行应用
if __name__ == '__main__':
    app.run(debug=True, port=5000)
