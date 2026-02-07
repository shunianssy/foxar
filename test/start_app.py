import subprocess
import sys

# 使用uvicorn直接运行应用
cmd = [sys.executable, "-m", "uvicorn", "example_app:app", "--reload", "--port", "5000"]

print("Starting application with uvicorn...")
print(f"Command: {' '.join(cmd)}")

# 运行命令
subprocess.run(cmd)
