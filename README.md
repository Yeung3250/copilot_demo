# copilot_demo
AI对话机器人样例

运行 start.sh文件即可,其中有些环境变量可以自行配置，不配置也有试用的模型参数
### 注意：
#### 1.请先激活python的环境后再运行，建议使用python310版本
#### 2.windows环境要用git bash或者wsl运行，终端无法运行sh
~~~
sh start.sh
~~~

windows环境下想在终端运行也可以在终端按步骤运行
~~~
venv_name/Scripts/activate  # 激活python环境，根据你的环境路径，也可以自己先激活环境，这行就不需要

# 需要先cd 到项目根目录
pip install -r requirements.txt
python -m src.copilot.main
~~~

服务启动后，请访问 <http://127.0.0.1:8000/>


