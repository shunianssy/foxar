from typing import List, Callable, Any

class Signal:
    """信号类"""
    def __init__(self):
        self.receivers: List[Callable] = []
    
    def connect(self, receiver: Callable) -> Callable:
        """连接信号接收器"""
        if receiver not in self.receivers:
            self.receivers.append(receiver)
        return receiver
    
    def disconnect(self, receiver: Callable) -> None:
        """断开信号接收器"""
        if receiver in self.receivers:
            self.receivers.remove(receiver)
    
    def send(self, *args, **kwargs) -> List[Any]:
        """发送信号"""
        results = []
        for receiver in self.receivers:
            try:
                result = receiver(*args, **kwargs)
                results.append(result)
            except Exception as e:
                # 忽略接收器中的异常
                pass
        return results

# 定义常用信号
# 请求开始信号
request_started = Signal()

# 请求结束信号
request_finished = Signal()

# 请求异常信号
request_exception = Signal()

# 模板渲染开始信号
template_rendered = Signal()

# 应用上下文推送信号
appcontext_pushed = Signal()

# 应用上下文弹出信号
appcontext_popped = Signal()

# 消息闪现信号
message_flashed = Signal()

# 模板渲染前信号
before_render_template = Signal()

# 请求拆卸信号
teardown_request = Signal()

# 应用上下文拆卸信号
teardown_appcontext = Signal()

# 提供与 Flask 命名空间兼容的信号
class _Namespace:
    """命名空间类"""
    pass

# 创建 flask 命名空间
flask = _Namespace()

# 在命名空间中添加信号
flask.template_rendered = template_rendered
flask.request_started = request_started
flask.request_finished = request_finished
flask.request_exception = request_exception
flask.appcontext_pushed = appcontext_pushed
flask.appcontext_popped = appcontext_popped
flask.message_flashed = message_flashed
flask.before_render_template = before_render_template
flask.teardown_request = teardown_request
flask.teardown_appcontext = teardown_appcontext

# 提供与Flask兼容的信号导入
def signals_available() -> bool:
    """检查信号是否可用"""
    return True

__all__ = [
    'request_started',
    'request_finished',
    'request_exception',
    'template_rendered',
    'appcontext_pushed',
    'appcontext_popped',
    'message_flashed',
    'before_render_template',
    'teardown_request',
    'teardown_appcontext',
    'flask',
    'signals_available'
]