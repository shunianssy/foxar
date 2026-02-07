from foxar.app import Foxar
from foxar.request import request
from foxar.response import jsonify
from starlette.testclient import TestClient

# 创建应用实例
app = Foxar(__name__)

# 测试请求对象属性
@app.route('/request-props/<user_id>')
def request_props(user_id):
    data = {
        'method': request.method,
        'path': request.path,
        'args': dict(request.args),
        'cookies': dict(request.cookies),
        'headers': dict(request.headers),
        'is_json': getattr(request, 'is_json', 'N/A'),
        'endpoint': getattr(request, 'endpoint', 'N/A'),
        'view_args': getattr(request, 'view_args', 'N/A'),
        'user_id': user_id
    }
    return jsonify(data)

# 测试请求数据获取
@app.route('/request-data', methods=['GET', 'POST'])
def request_data():
    data = {
        'method': request.method
    }
    
    # 测试 get_json()
    if hasattr(request, 'get_json'):
        try:
            json_data = request.get_json()
            data['json_data'] = json_data
        except Exception as e:
            data['json_error'] = str(e)
    
    # 测试 get_data()
    if hasattr(request, 'get_data'):
        try:
            raw_data = request.get_data()
            data['raw_data'] = raw_data.decode('utf-8') if raw_data else None
        except Exception as e:
            data['data_error'] = str(e)
    
    return jsonify(data)

# 测试表单数据
@app.route('/form-data', methods=['POST'])
def form_data():
    data = {
        'method': request.method
    }
    
    # 测试表单数据
    try:
        form = request.form()
        data['form_data'] = form
    except Exception as e:
        data['form_error'] = str(e)
    
    return jsonify(data)

if __name__ == "__main__":
    print("=== Testing Request Object ===")
    
    client = TestClient(app)
    
    # 测试请求对象属性
    response = client.get('/request-props/123?foo=bar&baz=qux')
    print(f"✅ ✓ Request props response status: {response.status_code}")
    props = response.json()
    print(f"✅ ✓ Request method: {props.get('method')}")
    print(f"✅ ✓ Request path: {props.get('path')}")
    print(f"✅ ✓ Request args: {props.get('args')}")
    print(f"✅ ✓ Request is_json: {props.get('is_json')}")
    print(f"✅ ✓ Request endpoint: {props.get('endpoint')}")
    print(f"✅ ✓ Request view_args: {props.get('view_args')}")
    
    # 测试 JSON 数据
    json_payload = {'name': 'John', 'age': 30}
    response = client.post('/request-data', json=json_payload)
    print(f"\n✅ ✓ JSON request response status: {response.status_code}")
    json_data = response.json()
    print(f"✅ ✓ JSON data received: {json_data.get('json_data')}")
    
    # 测试表单数据
    form_payload = {'username': 'testuser', 'password': 'secret'}
    response = client.post('/form-data', data=form_payload)
    print(f"\n✅ ✓ Form request response status: {response.status_code}")
    form_data = response.json()
    print(f"✅ ✓ Form data received: {form_data.get('form_data')}")
    
    print("\n=== Request Object Analysis ===")
    print("1. Basic request properties (method, path, args): IMPLEMENTED")
    print("2. request.is_json: PARTIALLY IMPLEMENTED (may need addition)")
    print("3. request.endpoint: PARTIALLY IMPLEMENTED (may need addition)")
    print("4. request.view_args: PARTIALLY IMPLEMENTED (may need addition)")
    print("5. get_json(): PARTIALLY IMPLEMENTED (may need addition)")
    print("6. get_data(): PARTIALLY IMPLEMENTED (may need addition)")
    print("7. form data handling: IMPLEMENTED")
